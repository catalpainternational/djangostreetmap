[![CI](https://github.com/catalpainternational/djangostreetmap/actions/workflows/ci.yml/badge.svg)](https://github.com/catalpainternational/djangostreetmap/actions/workflows/ci.yml)

# DjangoStreetMap

DjangoStreetMap is a Django application to load OSM data into a PostGIS database
and deliver OSM data as MVT tiles.

## Stack

- Python 3.11+
- Django 5.2 LTS
- Pydantic 2
- PostGIS 3.4+ (Postgres 16 recommended)
- Package managed with [uv](https://github.com/astral-sh/uv)

## OpenStreetMap Vector Tiles

> "A vector tile is a lightweight data format for storing geospatial vector data"

For an introduction to MVT (Mapbox Vector Tiles) see the [mapbox docs](https://docs.mapbox.com/help/glossary/vector-tiles/).
For an introduction to OSM see [openstreetmap.org](https://www.openstreetmap.org/).

## Purpose

1. Import OSM data as Django models
2. Expose Django models as MVT geographic format data

Tile generation is much faster when geometry is in `srid=3857`.

## Prerequisites

You need the `gdal` libraries installed.

On Ubuntu:
```bash
sudo apt install binutils libproj-dev gdal-bin
```

Otherwise refer to the Django docs "Installing geospatial libraries".

## Adding to a Project

```bash
uv add djangostreetmap
```

Extend `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...,
    "django.contrib.gis",
    "djangostreetmap",
    "osmflex",
]
```

## (Recommended) Set your cache

You likely want a fast cache for tiles (e.g. Memcached). If not configured, the
default cache is used.

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": "127.0.0.1:11211",
    }
}
```

## Development

### Set up a PostGIS container

```bash
docker run --rm -d \
    --name djsm_postgis \
    -e POSTGRES_DB=postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=post1234 \
    -p 49155:5432 \
    postgis/postgis:16-3.4 \
    -c fsync=off -c shared_buffers=4096MB
```

### Install dependencies

```bash
uv sync --dev
```

### Run tests

```bash
uv run pytest
```

### Lint / format / type-check

```bash
uv run ruff check .
uv run ruff format .
uv run mypy djangostreetmap maplibre
```

### Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Releasing

Releases are automated via GitHub Actions (`.github/workflows/release.yml`) using
PyPI Trusted Publishing (OIDC). To cut a release:

1. Bump `version` in `pyproject.toml` on `main`; commit and merge.
2. Tag the merged commit with the same version (no `v` prefix):
   ```bash
   git tag 0.3.0 && git push origin 0.3.0
   ```
3. The workflow verifies the tag matches `pyproject.toml`, that the commit is on
   `main`, builds sdist + wheel, publishes to PyPI, and creates a GitHub Release
   with auto-generated notes.

One-time PyPI setup (maintainer): on the PyPI project page, add a Trusted
Publisher for the `catalpainternational/djangostreetmap` repo, workflow
`release.yml`, environment `pypi`.

## Writing Views

Subclass `TileLayerView` with `MvtQuery` layers:

```python
class RoadLayerView(TileLayerView):
    layers = [
        MvtQuery(
            table=OsmHighway._meta.db_table,
            attributes=["name"],
            filters=[f"\"highway\"='{road_class}'"],
            layer=road_class,
        )
        for road_class in ("primary", "secondary", "tertiary")
    ]
```

Register the URL:

```python
path("highways/<int:zoom>/<int:x>/<int:y>.pbf", RoadLayerView.as_view()),
```

## Importing OSM Data

Fetch a `.osm.pbf` extract (e.g. from [Geofabrik](https://download.geofabrik.de/)):

```bash
wget https://download.geofabrik.de/asia/east-timor-latest.osm.pbf
```

You need `osm2pgsql` >= 1.3. The `osmflex` app provides two management commands
to populate the models:

```bash
./manage.py run_osm2pgsql /path/to/east-timor-latest.osm.pbf
./manage.py import_from_pgosmflex
```

## Exploring Data

- Django admin: <http://localhost:8000/admin/osmflex>
- psql: `psql --host localhost --username postgres --port 49155`
- QGIS: add a Postgres connection to `localhost:49155`, database `postgres`.
