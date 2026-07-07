.PHONY: db-up db-down install migrate pbf import runserver clean help

PBF ?= ./pbf/east-timor-latest.osm.pbf
PBF_URL ?= https://download.geofabrik.de/asia/east-timor-latest.osm.pbf

help:
	@echo "Targets:"
	@echo "  db-up      start PostGIS container on :49155"
	@echo "  db-down    stop container"
	@echo "  install    uv sync"
	@echo "  migrate    apply migrations"
	@echo "  pbf        download $(PBF)"
	@echo "  import     run_osm2pgsql + import_from_pgosmflex --truncate"
	@echo "  runserver  Django dev server on :8000"

db-up:
	docker compose up -d
	@printf "waiting for postgres "; \
	for i in 1 2 3 4 5 6 7 8 9 10; do \
	  if docker compose exec -T postgis pg_isready -U postgres >/dev/null 2>&1; then echo " ready"; exit 0; fi; \
	  printf "."; sleep 1; \
	done; \
	echo " timeout"; exit 1

db-down:
	docker compose down -v

install:
	uv sync

migrate: install
	uv run python manage.py migrate

pbf:
	mkdir -p pbf
	@if [ ! -f "$(PBF)" ]; then \
	  echo "Fetching $(PBF_URL) -> $(PBF)"; \
	  curl -L -o "$(PBF)" "$(PBF_URL)"; \
	else \
	  echo "$(PBF) already present"; \
	fi

import: migrate pbf
	uv run python manage.py run_osm2pgsql "$(PBF)"
	uv run python manage.py import_from_pgosmflex --truncate

runserver: migrate
	uv run python manage.py runserver 0.0.0.0:8000

clean:
	rm -rf .venv pbf
