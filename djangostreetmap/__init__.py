"""djangostreetmap: Django app + helpers for serving OSM data as MVT / GeoJSON.

See ``docs/architecture.md`` for the tile pipeline and ``docs/api.md`` for a
full export list.

Django ORM classes (models, views) are intentionally NOT re-exported at
package level to keep ``import djangostreetmap`` cheap and to avoid tripping
Django's app-registry check. Import views directly from
:mod:`djangostreetmap.views` when subclassing.
"""

from djangostreetmap.annotations import (
    GeoJsonFeature,
    GeoJsonFeatureCollection,
    GeoJsonGeometry,
    GeoJsonSerializer,
    MultiGeoJsonSerializer,
    TileCache,
)
from djangostreetmap.functions import (
    AsFeature,
    AsFeatureCollection,
    AsGeoJson,
    Intersects,
    Simplify,
)
from djangostreetmap.tilegenerator import MvtQuery, Tile

__all__ = [
    "AsFeature",
    "AsFeatureCollection",
    "AsGeoJson",
    "GeoJsonFeature",
    "GeoJsonFeatureCollection",
    "GeoJsonGeometry",
    "GeoJsonSerializer",
    "Intersects",
    "MultiGeoJsonSerializer",
    "MvtQuery",
    "Simplify",
    "Tile",
    "TileCache",
]
