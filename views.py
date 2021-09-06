# from django.shortcuts import render
from typing import List, Optional

from django.core.cache import caches
from django.db import connection
from django.http.response import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView

from .models import OsmAdminBoundary, OsmHighway, OsmIslands, OsmIslandsAreas
from .tilegenerator import MvtQuery, OutOfZoomRangeException, Tile


class ExampleMapView(TemplateView):
    template_name = "leaflet_tile_layers.html"


class TileLayerView(View):
    """
    Handle generation and views of tile layers
    """

    layers: List[MvtQuery] = []
    cache_prefix: Optional[str] = None
    cache_timeout: int = 3600
    cache_name: str = "mvt_tile_cache"

    def get_layers(self, tile: Tile) -> List[MvtQuery]:
        """
        Override for dynamically determining tile content
        based on tile properties (most likely zoom)
        """
        return self.layers

    def _cache_key(self, tile: Tile) -> str:
        return f"{self.cache_prefix}-{tile.zoom}-{tile.x}-{tile.y}"

    def _generate_tile(self, tile: Tile):
        with connection.cursor() as cursor:
            tiles = b""
            for layer in self.get_layers(tile):
                try:
                    query = layer.as_mvt(tile)
                except OutOfZoomRangeException:
                    continue
                cursor.execute(query)
                tile_response = cursor.fetchone()
                if tile_response:
                    tiles += tile_response[0]
            return tiles

    def _get_or_set_from_cache(self, tile: Tile) -> bytes:

        if not self.cache_prefix:
            return self._generate_tile(tile)

        # If a specific cache is set for tiles, use it
        # for better performance
        try:
            cache = caches[self.cache_name]
        except KeyError:
            try:
                cache = caches["default"]
            except KeyError:
                return self._generate_tile(tile)

        if not cache:
            return self._generate_tile(tile)

        key = self._cache_key(tile)

        tiles = cache.get(key)
        if tiles is None:
            tiles = self._generate_tile(tile)
            cache.set(key, tiles, self.cache_timeout)
        return tiles

    def get(self, request, *args, **kwargs):
        tile = Tile(**kwargs)  # Expect to receive zoom, x, and y in kwargs
        tiles = self._get_or_set_from_cache(tile)
        return HttpResponse(content=tiles, content_type="application/binary")


class RoadLayerView(TileLayerView):
    cache_prefix = "roads"

    def get_layers(self, tile: Tile):
        layers = []
        for road_class, min_zoom in [
            # ("steps", 5),
            # ("bus_guideway", 5),
            # ("footway", 5),
            # ("services", 5),
            ("trunk", 3),
            ("road", 12),
            ("secondary", 5),
            ("trunk_link", 3),
            ("tertiary", 10),
            ("secondary_link", 5),
            ("tertiary_link", 10),
            ("primary", 3),
            ("residential", 12),
            ("primary_link", 12),
            ("track", 12),
            ("service", 12),
            ("unclassified", 12),
            ("path", 12),
        ]:
            layers.append(
                MvtQuery(
                    table=OsmHighway._meta.db_table,
                    attributes=["name", "highway"],
                    filters=[f"\"highway\"='{road_class}'"],
                    layer=road_class,
                    min_render_zoom=min_zoom,
                    transform=False,
                )
            )
        return layers


class AdminBoundaryLayerView(TileLayerView):
    cache_prefix = "admin"
    layers = [MvtQuery(table=OsmAdminBoundary._meta.db_table, attributes=["name"], layer="admin_boundary")]


class IslandsLayerView(TileLayerView):
    cache_prefix = "islands"
    layers = [MvtQuery(table=OsmIslands._meta.db_table, attributes=["name"], layer="islands")]


class IslandsAreaLayerView(TileLayerView):
    cache_prefix = "islands_area"
    layers = [MvtQuery(table=OsmIslandsAreas._meta.db_table, attributes=["name"], layer="islands")]
