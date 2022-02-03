from typing import Any, Dict, Type

import django
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import GeoFunc
from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models import F, Value
from django.db.models.expressions import RawSQL

if django.VERSION >= (3, 2):
    from django.db.models.functions.comparison import JSONObject  # type: ignore
else:
    from .json_object import JSONObject

"""
Functions to generate JSON features & collections
directly from the database
"""


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

    # The cast to jsonb is required here as ST_AsGeoJSON actually puts out text
    template = "%(function)s(%(expressions)s)::jsonb"
    output_field = models.JSONField()


class AsFeature(JSONObject):
    def __init__(self, geom_field: str = "geom", **fields: Dict[str, Any]):
        expressions = [
            Value("type"),
            Value("Feature"),
            Value(
                "id",
            ),
            F("pk"),
            Value("geometry"),
            AsGeoJson(geom_field),
            Value("properties"),
            JSONObject(**fields),
        ]
        super(JSONObject, self).__init__(*expressions)


class AsFeatureCollection(JSONObject):
    def __init__(self, geom_field: str = "geom", **fields: Dict[str, Any]):
        expressions = [Value("type"), Value("FeatureCollection"), Value("features"), JSONBAgg(AsFeature(geom_field, **fields), default=Value("[]"))]
        super(JSONObject, self).__init__(*expressions)


class Simplify(GeoFunc):
    """
    Django has a simplify but that's for GEOS not
    for postgres
    """

    def __init__(self, expression, tolerance: float, **extra):
        expressions = [expression]
        if tolerance is not None:
            expressions.append(tolerance)
        super().__init__(*expressions, **extra)

    function = "ST_SimplifyPreserveTopology"
    output_field = models.GeometryField()


class Intersects(RawSQL):
    """
    Relate two separate geographic tables
    This intended for OSM data so SRID is assumed to require transform from 4326 to 3857
    """

    def __init__(self, instance: Type[models.Model], relation: str = "ST_INTERSECTS", target_geom_field: str = "geom", geom_field: str = "geom", srid: int = 3857):

        pk_field = instance._meta.pk
        assert pk_field

        return super().__init__(
            sql=f"""SELECT {relation}(
                    "{target_geom_field}",
                    (SELECT ST_TRANSFORM("{geom_field}", {srid}) FROM "{instance._meta.db_table}" WHERE "{pk_field.name}"=%s)
                )""",
            params=(instance.pk,),
        )
