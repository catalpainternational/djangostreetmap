This is a Django application to expose OpenStreetMap data

# Set up postgis

docker run --name=osm -e POSTGRES_PASSWORD=osm -P postgis/postgis:12-3.1

# Find your port

```
(env) josh@m4800:~/github/joshbrooks/djangostreetmap$ docker ps
CONTAINER ID   IMAGE                            COMMAND                  CREATED          STATUS             PORTS                                         NAMES
c619232fe38a   postgis/postgis:12-3.1           "docker-entrypoint.s…"   33 seconds ago   Up 32 seconds      0.0.0.0:49155->5432/tcp, :::49155->5432/tcp   osm
...
```

OSM is on port 49155

# Fetch your data

wget https://download.geofabrik.de/australia-oceania/papua-new-guinea-latest.osm.pbf

wget https://raw.githubusercontent.com/gravitystorm/openstreetmap-carto/master/openstreetmap-carto.style

# Load your data

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

# Exploring data

psql --host localhost --username postgres --port 49155

# Add ID's to the planet tables

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

## Qgis

-   Add a new Postgres Connection with the following settings:

Name: Papua New Guinea Roads
Host: localhost
Port: 49155
Database: postgres

Authentication: Basic
postgres / osm

# Add to a Project

start a new Django project

django-admin startproject osmfun
cd osmfun
git init .
git submodule add /home/josh/github/joshbrooks/djangostreetmap djangostreetmap

Set the settings of new project to match the above

in osmfun/settings.py:

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

Extend installed_apps with the following apps:

```python
[
    'django.contrib.gis',
    "djangostreetmap",
]
```
