# Architecture

`djangostreetmap` serves OpenStreetMap-derived data as **MVT vector tiles**
and **GeoJSON** by rendering PostgreSQL/PostGIS queries via the Django ORM
and the `psycopg2.sql` composable interface. This document walks the tile
pipeline, the SQL generation approach, and the extension points.

## Tile pipeline

```
    HTTP GET /roads/14/14891/8624.pbf
                │
                ▼
    ┌──────────────────────────┐
    │  TileLayerView.get()     │  parses {zoom,x,y} into Tile(dataclass)
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │  self.get_layers(tile)   │  returns list[MvtQuery] — override this
    └──────────┬───────────────┘  in subclasses for zoom-dependent behavior
               │
               ▼
    ┌──────────────────────────┐
    │  MvtQuery.as_mvt()       │  composes CTE + ST_AsMVTGeom + ST_AsMVT
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │  connection.cursor()     │  executes with `params = asdict(tile)`
    │      .execute(query)     │  → row[0] is a memoryview of MVT bytes
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │  optional: TileCache.set │  by SHA-256 of (query, params)
    └──────────┬───────────────┘
               │
               ▼
    HttpResponse(bytes,
                 content_type="application/binary")
```

## `MvtQuery`

A dataclass in [`djangostreetmap/tilegenerator.py`](../djangostreetmap/tilegenerator.py)
that composes a PostgreSQL query producing MVT bytes. Two constructors:

- **`MvtQuery(table=..., attributes=..., filters=..., ...)`** — raw table
  reference. Use this when you want a fixed table and a bounded set of
  attributes, e.g. `osmflex_roadline` with a whitelist of columns.
- **`MvtQuery.from_model(SomeModel)`** — introspects the model for its
  geometry field, PK, and non-geometry columns; picks `transform=True` if
  the SRID isn't already 3857.
- **`MvtQuery.from_queryset(queryset)`** — takes an arbitrary Django queryset
  (with `.filter()`, `.annotate()`, `.values()`) and wraps its rendered SQL
  as a CTE. Positional `%s` placeholders in Django's output are rewritten to
  named `%(param_N)s` and threaded through via `query_params`.

The wire format is unaffected by which constructor you use — the difference
is the ergonomics of expressing the source rows.

### The tile envelope + margin

`ST_AsMVTGeom` needs to know the tile bounding box. `MvtQuery` uses
`ST_TileEnvelope(z, x, y, margin => buffer/extent)` (PostGIS 3.1+) so features
straddling the tile boundary are still fetched — required for correct MVT
clipping. The `buffer` and `extent` come from the `Tile` dataclass and default
to 64/4096, matching Mapbox conventions.

## SRID choices

The default assumption is that source tables store geometry in **EPSG:3857**
(matching `osmflex` and the MVT output format). If your source is in another
SRID, pass `transform=True` to `MvtQuery`; it wraps the geometry column in
`ST_TRANSFORM(..., 3857)` at query time. `.from_model()` auto-detects this by
inspecting the field SRID.

## Cache protocol

`TileLayerView` takes an optional `tilecache: TileCache | None` — a
[Protocol](../djangostreetmap/annotations.py) that requires `.get(key)` and
`.set(key, value)`. Django's `django.core.cache.caches['default']` satisfies
it directly; you can also wire memcached or Redis. Cache keys are 8-char
SHA-256 prefixes of the concatenated `(query, params)` string.

## Writing a tile view

```python
from django.urls import path
from djangostreetmap import MvtQuery
from djangostreetmap.views import TileLayerView


class HighwaysLayer(TileLayerView):
    layers = [
        MvtQuery(
            table="osmflex_roadline",
            attributes=["name", "osm_type"],
            layer="transportation",
            pk="osm_id",
        )
    ]


urlpatterns = [
    path(
        "highways/<int:zoom>/<int:x>/<int:y>.pbf",
        HighwaysLayer.as_view(),
        name="highways",
    ),
]
```

For zoom-dependent layer selection, override `get_layers(tile)` instead of
setting the class attribute — see `djangostreetmap.views.BuildingPolygon`
(hidden below zoom 14) or `Roads` (per-class-min-zoom filter) for reference.

## GeoJSON path

Not everything needs to be a tile. `annotations.GeoJsonSerializer` renders
a `FeatureCollection` from a queryset with an annotated geometry column and
a small set of properties. `MultiGeoJsonSerializer` concatenates several
serializers into one collection — used for e.g. hospital points + hospital
polygon centroids surfaced through the same layer.

For SQL-side FeatureCollection aggregation (all work in the DB, one row out),
`djangostreetmap.functions.AsFeatureCollection` is a `JSONObject` subclass
using `JSONB_AGG` and PostGIS's `ST_AsGeoJson`. Use this when you want to
bypass Python-side iteration.

## `maplibre/` sub-package

Pydantic v2 models mirroring the MapLibre / Mapbox GL style spec. The
`MapStyle` view uses `maplibre.Root`, `maplibre.layer.Layer`, and
`maplibre.sources.Vector` to build a style JSON that references this app's
own tile endpoints. See [`docs/api.md`](./api.md#maplibre) for the export list.
