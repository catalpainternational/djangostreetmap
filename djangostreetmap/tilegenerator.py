import re
from dataclasses import dataclass, field
from itertools import count
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Union

from django.contrib.gis.db.models import GeometryField
from psycopg2 import sql

# To time mvt queries uncomment the following
# from .timer import Timer


@dataclass
class Tile:
    """
    Simple dataclass representing a "tile" instance and additional metadata
    for tile generation: buffer, extent and margin
    http://postgis.net/docs/ST_TileEnvelope.html

    """

    zoom: int
    x: int
    y: int
    buffer: int = 64
    extent: int = 4096

    @staticmethod
    def tile_envelope() -> sql.Composable:
        return sql.SQL("ST_TileEnvelope(%(zoom)s, %(x)s, %(y)s)")

    @staticmethod
    def tile_envelope_margin() -> sql.Composable:
        """
        Returns the ST_TileEnvelope function with a margin
        Note that the margin is only available in postgis 3.1+
        """
        return sql.SQL("ST_TileEnvelope(%(zoom)s, %(x)s, %(y)s, margin => (%(buffer)s / %(extent)s))")


@dataclass
class MvtQuery:
    """
    This is a SQL query generator based on the example
    at https://postgis.net/docs/manual-dev/ST_AsMVT.html
    """

    table: Union[str, sql.Composed, sql.SQL, sql.Identifier]
    # cte's are used to add additional WITH statements. This allows more flexibility in
    # adding Django querysets as MVT layers.
    ctes: Iterable[Tuple[sql.Identifier, Any]] = ()
    # When adding Django querysets with parameters, eg when filtering, there are
    # positional placeholders. These must be converted to named placeholders and included
    # in the `query_params` dict below for the final SQL statement to be correctly
    # handled.
    query_params: Dict[str, Any] = field(default_factory=dict)  # These are args to pass to any internal queryset we use where `table` is a Django queryset
    attributes: List[str] = field(default_factory=list)
    calculated_attributes: Dict[str, Union[sql.Composed, sql.SQL]] = field(default_factory=dict)
    filters: Sequence[sql.Composable] = field(default_factory=list)
    transform: bool = False  # Set to True if source srid is not 3857, but beware performance
    field: str = "geom"
    pk: str = "id"
    layer: str = "default"

    @property
    def json_attributes(self) -> sql.Composed:
        """
        Create a "JSONB_BUILD_OBJECT" clause
        """
        if not self.attributes and not self.calculated_attributes:
            return sql.SQL("").format()
        params = None
        for a in self.attributes:
            if not params:
                params = sql.Literal(a)
            else:
                params += sql.Literal(a)  # Name of the key is the same as the field
            params += sql.Identifier(a)  # The field to use as the value for the JSON

        for field, expression in self.calculated_attributes.items():
            if not params:
                params = sql.Literal(field)
            else:
                params += sql.Literal(field)  # Name of the key is the same as the field
            assert params
            params += expression  # The expression to use as the value for the JSON

        composed_params = params.join(", ")  # type: ignore

        return sql.SQL(", jsonb_build_object({})").format(composed_params)

    @property
    def transformed_geom(self) -> sql.Composable:
        """
        Return an `ST_TRANSFORM` clause
        https://postgis.net/docs/ST_Transform.html
        """
        template = "{field}"
        if self.transform:
            template = f"ST_TRANSFORM({template}, 3857)"
        return sql.SQL(template).format(field=sql.Identifier(self.field))

    @property
    def alias(self) -> sql.Composable:
        """
        The name of the query alias to use for postgresql
        """
        return sql.Identifier(f"mvt_{self.layer}")

    @property
    def where(self) -> sql.Composable:
        return sql.SQL(" AND ") + sql.SQL(" AND ").join(self.filters) if self.filters else sql.SQL("")

    @property
    def as_mvtgeom(self) -> sql.Composable:
        return sql.SQL(
            """
            ST_AsMVTGeom(
                {cg},
                {e},
                extent => %(extent)s,
                buffer => %(buffer)s
            ) AS geom, {pk} {json_attributes}
            FROM {t}
            WHERE {where}
            """
        ).format(
            cg=self.transformed_geom,
            e=Tile.tile_envelope(),
            t=sql.Identifier(self.table) if isinstance(self.table, str) else self.table,
            # Properties of "self"
            pk=sql.Identifier(self.pk),
            json_attributes=self.json_attributes,
            where=self._feature_query,
        )

    @property
    def _feature_query(self) -> sql.Composable:
        """
        Return the sql required for the geometry query
        and other specified filters
        """
        return sql.SQL("""{g} && {m} {where}""").format(
            g=self.transformed_geom,
            m=Tile.tile_envelope(),
            # TODO: Re enable the margin when postgis >= 3.1
            # m=Tile.tile_envelope_margin(),
            where=self.where,
        )

    def get_cte_sql(self) -> sql.Composed:
        """
        The common table expressions we use, composed to
        an appropriate format for the query
        """

        gen = (sql.SQL("{} AS (select {})").format(*_cte) for _cte in (*self.ctes, ((self.alias, self.as_mvtgeom))))
        return (sql.SQL("WITH ") + sql.SQL(",").join(gen)).join(" ")

    def as_mvt(self) -> sql.Composed:
        outer_query = self.get_cte_sql()
        inner_query = sql.SQL(" SELECT ST_AsMVT( {alias}.*, {layer}, %(extent)s, 'geom', {pk}) FROM {alias}" "")
        parameters = dict(alias=self.alias, layer=sql.Literal(self.layer), inner_query=self.as_mvtgeom, pk=sql.Literal(self.pk))
        return (outer_query + inner_query.format(**parameters)).join(" ")

    @classmethod
    def from_model(cls, model, *args, **kwargs) -> "MvtQuery":

        field = kwargs.pop("field", get_geom_field(model))
        attributes = kwargs.pop("attributes", get_model_attributes(model))
        pk = kwargs.get("pk", get_model_pk_field(model))
        transform = model._meta.get_field(field).srid != 3857
        return cls(table=model._meta.db_table, attributes=attributes, field=field, transform=transform, pk=pk, layer=kwargs.pop("layer", model._meta.model_name), **kwargs)

    @classmethod
    def from_queryset(cls, queryset, field: str = "geom", attributes: List[str] = ["id"], pk: str = "id", transform: bool = False, *args, **kwargs) -> "MvtQuery":
        """
        Takes as input a Django queryset
        This requires more configureation than calling from a model
        as querysets are a little harder to introspect
        """
        # Replace some parts of the Django sql
        # to make it work as a CTE
        django_sql, query_params = convert_to_positional_query(queryset)

        # Our django queryset will become a common table expression AKA "with" statement
        cte_name = sql.Identifier("django_queryset")
        if django_sql.startswith("SELECT"):
            django_sql = django_sql[6:]
        django_sql = django_sql.replace("::bytea", "")

        instance = cls(
            table=cte_name,
            ctes=((cte_name, sql.SQL(django_sql)),),
            query_params=query_params,
            attributes=attributes,
            field=field,
            transform=transform,
            pk=pk,
            layer=kwargs.pop("layer", queryset.model._meta.model_name),
            **kwargs,
        )
        return instance


def get_geom_field(model) -> str:
    """
    Returns the first field likely to be a geometry field
    from a model
    """
    fields = model._meta.fields  # type: List
    for field_ in fields:
        if isinstance(field_, GeometryField):
            return field_.db_column or field_.attname
    raise KeyError(f"No geometry field could be identified for {model}")


def get_model_attributes(model) -> List[str]:
    """
    Returns the columns of a model
    """
    fields = model._meta.fields  # type: List
    return [f.db_column or f.attname for f in fields if not isinstance(f, GeometryField)]


def get_model_pk_field(model) -> str:
    fields = model._meta.fields  # type: List
    for pk_field_candidate in fields:
        if pk_field_candidate.primary_key:
            return pk_field_candidate.db_column or pk_field_candidate.attname
    raise KeyError(f"No primary key field could be identified for {model}")


def convert_to_positional_query(queryset):
    """
    From a Django queryset, convert the placeholders to named ones
    in order to enable combining with other parts of this module
    """
    # Initialise a new counter for the named parameters
    c = count()
    django_sql, args = queryset.query.sql_with_params()
    positional_sql = re.sub("%s", lambda x: f"%(param_{next(c)})s", django_sql)
    query_params = {f"param_{i}": param for i, param in enumerate(args)}
    return positional_sql, query_params
