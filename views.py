# from django.shortcuts import render
from typing import List, Optional

from django.core.cache import cache
from django.db import connection
from django.http.response import HttpResponse
from django.views import View

from .models import OsmAdminBoundary, OsmHighway, OsmIslands, OsmIslandsAreas
from .tilegenerator import MvtQuery, Tile


class TileLayerView(View):
    """
    Handle generation and views of tile layers
    """

    layers: List[MvtQuery] = []
    cache_prefix: Optional[str] = None
    cache_timeout: int = 3600

    def _cache_key(self, tile: Tile) -> str:
        return f"{self.cache_prefix}-{tile.zoom}-{tile.x}-{tile.y}"

    def _generate_tile(self, tile: Tile):
        with connection.cursor() as cursor:
            tiles = b""
            for layer in self.layers:
                cursor.execute(layer.as_mvt(tile))
                tile_response = cursor.fetchone()
                if tile_response:
                    tiles += tile_response[0]
            return tiles

    def _get_or_set_from_cache(self, tile: Tile) -> bytes:
        key = self._cache_key(tile)
        if not self.cache_prefix:
            return self._generate_tile(tile)

        tiles = cache.get(key)
        if tiles is not None:
            tiles = self._generate_tile(tile)
            cache.set(key, tiles, self.cache_timeout)
        return tiles

    def get(self, request, *args, **kwargs):
        tile = Tile(**kwargs)  # Expect to receive zoom, x, and y in kwargs
        tiles = self._get_or_set_from_cache(tile)
        return HttpResponse(content=tiles, content_type="application/binary")


class RoadLayerView(TileLayerView):
    layers = [
        MvtQuery(table=OsmHighway._meta.db_table, attributes=["name"], filters=[f"\"highway\"='{road_class}'"], layer=road_class)
        for road_class in ("primary", "secondary", "tertiary")
    ]


class AdminBoundaryLayerView(TileLayerView):
    layers = [MvtQuery(table=OsmAdminBoundary._meta.db_table, attributes=["name"], layer="admin_boundary")]


class IslandsLayerView(TileLayerView):
    layers = [MvtQuery(table=OsmIslands._meta.db_table, attributes=["name"], layer="islands")]


class IslandsAreaLayerView(TileLayerView):
    layers = [MvtQuery(table=OsmIslandsAreas._meta.db_table, attributes=["name"], layer="islands")]
