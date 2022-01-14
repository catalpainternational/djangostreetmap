from dataclasses import dataclass, field
from typing import Dict, List, Optional

from django.db import connection
from django.db.models.base import Model
from django.db.models.query import QuerySet

PgFunction = str


class OutOfZoomRangeException(Exception):
    """
    Raised when a renderer layer receives
    a tile outside of its zoom range settings
    """

    pass


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
    margin: str = "(64 / 4096)"

    @property
    def envelope(self) -> str:
        return f"{self.zoom}, {self.x}, {self.y}"

    @property
    def tile_envelope(self) -> PgFunction:
        return f"ST_TileEnvelope({self.envelope})"

    @property
    def tile_envelope_margin(self) -> PgFunction:
        return f"ST_TileEnvelope({self.envelope}, margin => {self.margin})"


@dataclass
class MvtQuery:
    """
    This is a SQL query generator based on the example
    at https://postgis.net/docs/manual-dev/ST_AsMVT.html
    """

    table: Optional[str] = None
    model: Optional[Model] = None
    queryset: Optional[QuerySet] = None
    attributes: List[str] = field(default_factory=list)
    attribute_map: Dict[str, str] = field(default_factory=dict)
    filters: List[str] = field(default_factory=list)
    transform: bool = False  # Set to True if source srid is not 3857, but beware performanc
    field: str = "geom"
    pk: str = "id"
    layer: str = "default"
    min_render_zoom: Optional[int] = None
    max_render_zoom: Optional[int] = None

    @property
    def json_attributes(self) -> PgFunction:
        """
        Compiles a jsonb_build_object clause from attributes
        Returns a `JSONB_BUILD_OBJECT` function clause
        """
        statements = []
        for attr in self.attributes:
            statements.extend([f"'{attr}'", f'"{attr}"'])
        for attr_k, attr_v in self.attribute_map.items():
            statements.extend([f"'{attr_k}'", f"{attr_v}"])
        joined = ", ".join(statements)
        return f", jsonb_build_object({joined}) " if self.attributes or self.attribute_map else ""

    @property
    def transformed_geom(self) -> PgFunction:
        """
        Return an `ST_TRANSFORM` clause
        https://postgis.net/docs/ST_Transform.html
        """
        if self.transform:
            return f"ST_TRANSFORM({self.field}, 3857)"
        return self.field

    @property
    def alias(self):
        """
        The name of the query alias to use for postgresql
        """
        return f"mvt_{self.layer}"

    @property
    def table_or_queryset(self):

        if self.table:
            return self.table

        if self.model:
            return self.model._meta.db_table

        if isinstance(self.queryset, QuerySet):
            query, params = self.queryset.query.sql_with_params()
            with connection.cursor() as c:
                # Wrap the queryset in a cursor

                # Workaround - Django casts geom to bytea which horribly impacts performance
                # See The `PostGISOperations` class for the place where this occurs
                query = query.replace("::bytea", "")
                c.mogrify(query, params).decode()

                return "(%s) AS queryset" % (c.mogrify(query, params).decode(),)

    def as_mvtgeom(self, tile: Tile) -> PgFunction:
        where = [f"{self.transformed_geom} && {tile.tile_envelope_margin}"]
        where.extend(self.filters)
        where_clause = " AND ".join(where)

        return f"""
        ST_AsMVTGeom(
              {self.transformed_geom},
              {tile.tile_envelope},
              extent => {tile.extent},
              buffer => {tile.buffer}
        ) AS geom, "{self.pk}" {self.json_attributes}
          FROM {self.table_or_queryset}
          WHERE {where_clause}
        """

    def as_mvt(self, tile: Tile) -> PgFunction:
        if self.min_render_zoom and tile.zoom < self.min_render_zoom:
            raise OutOfZoomRangeException
        if self.max_render_zoom and tile.zoom > self.max_render_zoom:
            raise OutOfZoomRangeException
        return f"WITH {self.alias} AS (SELECT {self.as_mvtgeom(tile)}) SELECT ST_AsMVT({self.alias}.*, '{self.layer}', {tile.extent}, 'geom', '{self.pk}') FROM {self.alias}"

    def execute(self, tile: Tile):
        with connection.cursor() as c:
            try:
                c.execute(self.as_mvt(tile))
            except OutOfZoomRangeException:
                return b""
            tile_response = c.fetchone()
            return tile_response
