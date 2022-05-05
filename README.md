[![codecov](https://codecov.io/gh/joshbrooks/djangostreetmap/branch/main/graph/badge.svg?token=MXcJUkbOMf)](https://codecov.io/gh/joshbrooks/djangostreetmap)

# DjangoStreetMap

DjangSstreetMap is a Django application to load OSM data into a postgis database and deliver OSM data as
MVT tiles.

## Openstreetmap Vector Tiles

> "A vector tile is a lightweight data format for storing geospatial vector data"

For an introduction to MVT (Mapbox Vector Tiles) see the [mapbox docs](https://docs.mapbox.com/help/glossary/vector-tiles/)
For an introduction to OSM see [openstreetmap.org](https://www.openstreetmap.org/)

## Purpose of this project

This is a Django application to

1. Import OSM data as Django models
2. Expose Django models as MVT (Mapbox Vector Tile) geographic format data

Tile generation is much faster when geometry is in srid=3857 (or maybe with an index in that SRID?)

## Prerequisites

You need the `gdal` libraries installed

On Ubuntu:
```
sudo apt install binutils libproj-dev gdal-bin
```

Otherwise refer to the Django docs "Installing geospatial libraries"
## Adding to a Project

If necessary install psycopg2 in your env

Extend installed_apps with the following apps:

`pip install osmflex`

```python
[
    "django.contrib.gis",
    "djangostreetmap",
    "osmflex",
]
```

## (Recommended) Set your cache

You likely want to set a fast cache for your tiles like Memcached. If this is not found
the default cache will be used; this can be a bit slower and is very much non persistent
This assumes you're running memcached (Linux: `apt install memcached`) and installed memcached(`pip install python-memcached`)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

## Running faster in testing

Run `poetry install`

To run pytest, you need to have an appropriate postgis database
If you use docker one option is to run the following:

```bash
docker run \
    --rm \
    -p 49155:5432 \
    --name=djangostreetmap \
    -e POSTGRES_PASSWORD=post1234 \
    postgis/postgis:14-3.2 \
    -c fsync=off \
    -c shared_buffers=4096MB
```
Run `poetry run pytest`


Runserver is "ok" but this recipe will give faster performance for demonstration purposes



```bash
pip install gunicorn
gunicorn -w 8 djangostreetmap.wsgi:application
```

## Building

poetry version patch
poetry build
poetry publish

## Writing Views

To set up a new View, create a subclass of TileLayerView with some `MvtQuery` instances as layers:

```python
class RoadLayerView(TileLayerView):
    layers = [
        MvtQuery(table=OsmHighway._meta.db_table, attributes=["name"], filters=[f"\"highway\"='{road_class}'"], layer=road_class)
        for road_class in ("primary", "secondary", "tertiary")
    ]
```

Append the URL to your urls.py as follows. Note the zoom, x and y are mandatory.

```python
    path("highways/<int:zoom>/<int:x>/<int:y>.pbf", RoadLayerView.as_view()),
```

## Running in Development

### Set up postgis

```bash
docker run --name=osm \
    -e POSTGRES_DB=postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=post1234 \
    -p 49155:5432 \
    postgis/postgis:12-3.1
```

Find your port: if you do not use `49155` as above:

```sh
(env) josh@m4800:~/github/joshbrooks/djangostreetmap$ docker ps
CONTAINER ID   IMAGE                            COMMAND                  CREATED          STATUS             PORTS                                         NAMES
c619232fe38a   postgis/postgis:12-3.1           "docker-entrypoint.s…"   33 seconds ago   Up 32 seconds      0.0.0.0:49155->5432/tcp, :::49155->5432/tcp   osm
...
```

OSM is on port 49155

To apply this to your project:

```python
  DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "USER": "postgres",
        "PASSWORD": "post1233",
        "HOST": "localhost",
        "PORT": "49154",
        "NAME": "postgres",
    }
}
```

### Fetch your data

wget https://download.geofabrik.de/australia-oceania/papua-new-guinea-latest.osm.pbf

or

wget https://download.geofabrik.de/asia/east-timor-latest.osm.pbf

### Installing osm2psql

To run the management command below you'll need an `osm2pgsql` version of around 1.3 or greater. This is not available in the ubuntu package manager (yet)...

### Import Data

The "osmflex" app has two management commands to run which will populate osmflex models

```sh
./manage.py run_osm2pgsql /media/josh/blackgate/osm/asia/east-timor-latest.osm.pbf
```

```sh
./manage.py import_from_pgosmflex
```

### Exploring data

See the Django admin for osmflex:

http://localhost:8000/admin/osmflex

psql --host localhost --username postgres --port 49159

### Qgis

- Add a new Postgres Connection with the following settings:

Name: DjangoStreetMap
Host: localhost
Port: 49155
Database: postgres

Authentication: Basic
postgres / post1233

## Development

Code is blacked, flaked, isorted and mypy'd.

`pip install pre-commit`
