# Set up postgis

docker run --name=osm -e POSTGRES_PASSWORD=osm -P postgis/postgis:12-3.1

# Find your port

```
(env) josh@m4800:~/github/joshbrooks/djangostreetmap$ docker ps
CONTAINER ID   IMAGE                            COMMAND                  CREATED          STATUS             PORTS                                         NAMES
c619232fe38a   postgis/postgis:12-3.1           "docker-entrypoint.s…"   33 seconds ago   Up 32 seconds      0.0.0.0:49155->5432/tcp, :::49155->5432/tcp   osm
5776ce2a96da   ghcr.io/joshbrooks/openly_dird   "docker-entrypoint.s…"   3 weeks ago      Up 55 minutes      0.0.0.0:32774->5432/tcp, :::32774->5432/tcp   dird_test
812effd185b7   5e41922cc434                     "docker-entrypoint.s…"   4 weeks ago      Up About an hour   0.0.0.0:49153->5432/tcp, :::49153->5432/tcp   databases_plov_1
0593905bce24   5e41922cc434                     "docker-entrypoint.s…"   4 weeks ago      Up About an hour   0.0.0.0:32771->5432/tcp, :::32771->5432/tcp   databases_dird_1
90115c00149f   5e41922cc434                     "docker-entrypoint.s…"   4 weeks ago      Up About an hour   0.0.0.0:32769->5432/tcp, :::32769->5432/tcp   databases_mohinga_1
a46207132739   5e41922cc434                     "docker-entrypoint.s…"   4 weeks ago      Up About an hour   0.0.0.0:32776->5432/tcp, :::32776->5432/tcp   databases_mohinga_beta_1
7d02e926d173   5e41922cc434                     "docker-entrypoint.s…"   4 weeks ago      Up About an hour   0.0.0.0:32770->5432/tcp, :::32770->5432/tcp   databases_dird_production_1
```

OSM is on 49155

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

## Qgis

 - Add a new Postgres Connection with the following settings:

 Name: Papua New Guinea Roads
 Host: localhost
 Port: 49155
 Database: postgres

 Authentication: Basic
 postgres / osm
