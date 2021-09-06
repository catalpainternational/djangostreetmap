# Openstreetmap Vector Tiles


> "A vector tile is a lightweight data format for storing geospatial vector data"

For an introduction to MVT (Mapbox Vector Tiles) see the [mapbox docs](https://docs.mapbox.com/help/glossary/vector-tiles/)
For an introduction to OSM see [openstreetmap.org](https://www.openstreetmap.org/)

## Purpose of this project

This is a Django application to
 1) Import OSM data as Django models
 2) Expose Django models as MVT (Mapbox Vector Tile) geographic format data


# Adding to a Project

In your existing Django project, add this repo as a submodule:

```sh
git submodule add /home/josh/github/joshbrooks/djangostreetmap djangostreetmap
```
Set the settings of new project to match the above

Extend installed_apps with the following apps:

```python
[
    "django.contrib.gis",
    "djangostreetmap",
]
```

# Writing Views

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

docker run --name=osm -e POSTGRES_PASSWORD=osm -P postgis/postgis:12-3.1


Find your port:

```
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
    "NAME": "postgres",
    "USER": "postgres",
    "PASSWORD": "osm",
    "HOST": "localhost",
    "PORT": "49155",
    }
}
```

### Fetch your data

wget https://download.geofabrik.de/australia-oceania/papua-new-guinea-latest.osm.pbf

wget https://raw.githubusercontent.com/gravitystorm/openstreetmap-carto/master/openstreetmap-carto.style

### Load your data (1 - osm2pgsql)

This will populate the "auto" fields

osm2pgsql \
 --username postgres\
 --database postgres\
 --password\
 --host localhost\
 --port 49155\
 --style openstreetmap-carto.style\
 --proj 4326\
 --create\
 papua-new-guinea-latest.osm.pbf

### Load your data (Method 2 - Using osmium)

A simple handler for osmium might look like this:

```
class Handler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.factory = osmium.geom.WKBFactory()
        self.queryset = my_model.objects.all()  # type: QuerySet

    def area(self, area):
        if area.tags.get("place") == "island":
            self.areas.filter(id=area.id).delete()
            self.areas.create(
                id=area.id,
                geom=GEOSGeometry(self.factory.create_multipolygon(area)),
                name=area.tags.get("name", None),
            )

Handler().apply_file(path_to_file, locations=True)
```
You can then apply this in a Command like this:

```
class Command(BaseCommand):
    help = "Import roads from an OSM pbf file"

    def add_arguments(self, parser):
        parser.add_argument("osmfile", type=str, help="Path to the OSM file with the data to import")

    def handle(self, *args, **options):
        # HighwayHandler().apply_file(options["osmfile"], locations=True)
        # OsmAdminBoundaryHandler().apply_file(options["osmfile"], locations=True)
        OsmIslandsBoundaryHandler().apply_file(options["osmfile"], locations=True)
```

### Exploring data

psql --host localhost --username postgres --port 49155

### Add ID's to the planet tables

psql --host localhost --username postgres --port 49155

```sql
ALTER TABLE Planet_Osm_Line ADD COLUMN unique_id SERIAL PRIMARY KEY;
ALTER TABLE Planet_Osm_Point ADD COLUMN unique_id SERIAL PRIMARY KEY;
ALTER TABLE Planet_Osm_Polygon ADD COLUMN unique_id SERIAL PRIMARY KEY;
```

... and drop the useless roads table
it's duplicated in lines anyway and seems to miss a of road instances

```sql
DROP TABLE Planet_Osm_Roads;
```

### Qgis

-   Add a new Postgres Connection with the following settings:

Name: Papua New Guinea Roads
Host: localhost
Port: 49155
Database: postgres

Authentication: Basic
postgres / osm

# Development

Code is blacked, flaked, isorted and mypy'd.

`pip install pre-commit`
