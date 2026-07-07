# Minimal djangostreetmap tile server

A tiny standalone Django project that installs `djangostreetmap` + `osmflex`
from PyPI, imports an OSM extract, and serves MVT tiles at
`http://localhost:8000/tiles/<z>/<x>/<y>.pbf`. Not shipped in the
`djangostreetmap` wheel.

## Prerequisites

- Docker (PostGIS container)
- `osm2pgsql` ≥ 1.6 on the host
- Python ≥ 3.11 with `uv` (`pipx install uv` or
  `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Quick start

```bash
make db-up            # start postgis:16-3.4 on localhost:49155
make install          # uv venv + install deps
make migrate
make import           # download a small East Timor extract + run the two osmflex commands
make runserver        # Django dev server on :8000
```

Then in your browser (or `curl`), any of:

- <http://localhost:8000/tiles/roads/14/14891/8624.pbf>
- <http://localhost:8000/tiles/buildings/14/14891/8624.pbf>
- <http://localhost:8000/tiles/style>

The tile coords `14/14891/8624` cover Port Moresby — override in the URL for
wherever your imported PBF is located.

## Layout

```
examples/minimal/
├── Makefile
├── docker-compose.yml   # postgis on port 49155
├── manage.py
├── project/
│   ├── settings.py      # osmflex + djangostreetmap wired up
│   └── urls.py          # include djangostreetmap.urls under /tiles/
├── pyproject.toml       # deps: Django, osmflex, djangostreetmap, psycopg2
└── pbf/                 # PBF files download here (gitignored)
```

## Cleanup

```bash
make db-down          # tear down the container
make clean            # remove .venv/ and pbf/
```
