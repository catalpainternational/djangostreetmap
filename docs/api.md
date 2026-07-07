# API cheatsheet

Every public symbol at a glance. See [architecture.md](./architecture.md) for
how they fit together and [../examples/minimal/](../examples/minimal/) for a
runnable project.

## `djangostreetmap`

```python
from djangostreetmap import (
    Tile, MvtQuery,
    AsFeature, AsFeatureCollection, AsGeoJson, Intersects, Simplify,
    GeoJsonSerializer, MultiGeoJsonSerializer,
    GeoJsonFeature, GeoJsonFeatureCollection, GeoJsonGeometry,
    TileCache,
)
```

### Tile pipeline

| Name                | Kind      | Purpose                                                                                     |
| ------------------- | --------- | ------------------------------------------------------------------------------------------- |
| `Tile`              | dataclass | `zoom, x, y, buffer=64, extent=4096` — passed as query params.                              |
| `MvtQuery`          | dataclass | SQL generator for MVT tiles. Use `.from_model()` or `.from_queryset()` for the common cases. |

### ORM function wrappers (`djangostreetmap.functions`)

| Name                 | Kind     | Purpose                                                                    |
| -------------------- | -------- | -------------------------------------------------------------------------- |
| `AsGeoJson`          | GeoFunc  | Wraps `ST_AsGeoJson`. Emits `jsonb` (not `text`).                          |
| `AsFeature`          | JSONObject | Renders one row as a GeoJSON `Feature`.                                    |
| `AsFeatureCollection`| JSONObject | Aggregates a queryset into a GeoJSON `FeatureCollection` via `JSONB_AGG`. |
| `Simplify`           | GeoFunc  | Wraps `ST_SimplifyPreserveTopology`.                                        |
| `Intersects`         | RawSQL   | Filters one model by intersection against another model's row geometry.     |

### GeoJSON serializers (`djangostreetmap.annotations`)

| Name                       | Kind      | Purpose                                                              |
| -------------------------- | --------- | -------------------------------------------------------------------- |
| `GeoJsonSerializer`        | dataclass | Iterates a queryset, emits `GeoJsonFeatureCollection` in Python.     |
| `MultiGeoJsonSerializer`   | dataclass | Concatenates multiple `GeoJsonSerializer`s into one collection.     |
| `GeoJsonFeature`           | dataclass | Simple `type, geometry, properties` dataclass.                       |
| `GeoJsonFeatureCollection` | dataclass | Simple `type, features` dataclass.                                    |
| `GeoJsonGeometry`          | dataclass | Simple `type, coordinates` dataclass.                                 |
| `TileCache`                | Protocol  | Required interface for a tile cache: `.get(key)` / `.set(key, val)`. |

### Views (`djangostreetmap.views`)

Not re-exported at package level (import from `djangostreetmap.views`).

- `TileLayerView` — base class for MVT endpoints. Override `get_layers(tile)`.
- `Roads`, `BuildingPolygon`, `LandLayer`, `PoiLayer` — concrete tile views.
- `Hospitals`, `Aeroways` — non-tile GeoJSON views.
- `MapStyle` — returns a MapLibre style JSON that references the above.
- `ExampleMapView` — template view for `leaflet_tile_layers.html`.

## `maplibre`

```python
from maplibre import (
    Root, Layer, Layout, Paint, BackgroundPaint,
    Vector, Raster, RasterDem, GeoJson, Image, Video, Source, AnySource,
    Light, Anchor, Sprite, Transition,
)
```

Pydantic v2 models for the MapLibre / Mapbox style spec. Every field carries a
`description=...` matching the upstream spec.

| Name                                        | Purpose                                                       |
| ------------------------------------------- | ------------------------------------------------------------- |
| `Root`                                      | Top-level style: `version`, `sources`, `layers`, ...           |
| `Layer`, `Layout`, `Paint`, `BackgroundPaint` | Layer + rendering rules.                                     |
| `Vector`, `Raster`, `RasterDem`, `GeoJson`, `Image`, `Video` | Source types, discriminated on `type`.  |
| `Source`, `AnySource`                       | Base + tagged union of all source types.                       |
| `Light`, `Anchor`                           | 3D lighting spec.                                              |
| `Sprite`, `Transition`                      | Sprite atlas + transition timing.                              |

### Parsing / dumping

```python
from maplibre import Root
style = Root.model_validate_json(open("style.json").read())
serialised = style.model_dump_json(exclude_unset=True, by_alias=True)
```

`by_alias=True` matters — the MapLibre spec uses kebab-case (`source-layer`,
`background-color`), while the Python classes use camelCase attribute names.
