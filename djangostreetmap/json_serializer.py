from typing import Any, Dict
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import GeoFunc, Transform
from django.db import NotSupportedError
from django.db.models import Func, Value


class JSONObject(Func):
    """
    This is backported from Django 4
    to provide an easier way to generate the "Properties" dict
    """

    function = "JSON_OBJECT"
    output_field = models.JSONField()

    def __init__(self, **fields: Dict[str, Any]):
        expressions = []
        for key, value in fields.items():
            expressions.extend((Value(key), value))
        super().__init__(*expressions)

    def as_sql(self, compiler, connection, **extra_context):
        if not connection.features.has_json_object_function:
            raise NotSupportedError("JSONObject() is not supported on this database backend.")
        return super().as_sql(compiler, connection, **extra_context)

    def as_postgresql(self, compiler, connection, **extra_context):
        return self.as_sql(
            compiler,
            connection,
            function="JSONB_BUILD_OBJECT",
            **extra_context,
        )

    def as_oracle(self, compiler, connection, **extra_context):
        class ArgJoiner:
            def join(self, args):
                args = [" VALUE ".join(arg) for arg in zip(args[::2], args[1::2])]
                return ", ".join(args)

        return self.as_sql(
            compiler,
            connection,
            arg_joiner=ArgJoiner(),
            template="%(function)s(%(expressions)s RETURNING CLOB)",
            **extra_context,
        )


class AsGeoJson(GeoFunc):
    """
    This returns a geometry as JSON
    """

    def __init__(self, expression, maxdecimaldigits=6, **extra):
        expressions = [expression]
        if maxdecimaldigits is not None:
            expressions.append(self._handle_param(maxdecimaldigits, "maxdecimaldigits", int))
        super().__init__(*expressions, **extra)

    function = "ST_AsGeoJson"
    output_field = models.JSONField()


class Simplify(GeoFunc):
    def __init__(self, expression, tolerance: float, preserve_collapsed: bool, **extra):
        expressions = [expression]
        if tolerance is not None:
            expressions.append(self._handle_param(tolerance, "tolerance", float))
        if preserve_collapsed is not None:
            expressions.append(self._handle_param(preserve_collapsed, "preserve_collapsed", float))
        super().__init__(*expressions, **extra)

    function = "ST_SimplifyPreserveTopology"
    output_field = models.GeometryField()


class GeoSerializer:
    """
    Django's GeoJSON serializer returns string directly
    and cannot handle functions as geometry output
    """

    def geo_func(self, geom_field:str = "geom") -> GeoFunc:
        """
        For lines / polygons, you may wish to override
        this with a simplification
        """
        return AsGeoJson(Transform(geom_field, 4326), maxdecimaldigits=6)

    def feature_func(self, **fields: Dict[str, Any]) -> Func:
        """
        Returns a JSONB object
        """
        return JSONObject(**fields)

    def serialize(self, queryset: models.QuerySet[Any], geom_field: str = "geom", **fields: Dict[str, Any]):
        """
        Return Point features as GeoJson
        """
        return {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "geometry": qs.geometry, "properties": qs.properties}
                for qs in queryset.annotate(geometry=self.geo_func(geom_field), properties=self.feature_func(**fields))
            ],
        }
