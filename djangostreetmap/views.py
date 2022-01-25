from typing import List
from django.apps import apps

from django.db import connection
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.core.serializers import serialize

from .models import (
    FacebookAiRoad,
    OsmAdminBoundary,
    OsmHighway,
    OsmIslands,
    OsmIslandsAreas,
)
from .tilegenerator import MvtQuery, OutOfZoomRangeException, Tile


class ExampleMapView(TemplateView):
    template_name = "leaflet_tile_layers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["map_view"] = f"[-8.556416, 125.5524171], 14"
        return context


class TileLayerView(View):
    """
    Handle generation and views of tile layers
    """

    layers: List[MvtQuery] = []

    def get_layers(self, tile: Tile) -> List[MvtQuery]:
        """
        Override for dynamically determining tile content
        based on tile properties (most likely zoom)
        """
        return self.layers

    def _generate_tile(self, tile: Tile) -> bytes:
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

    def get(self, request, *args, **kwargs):
        tile = Tile(**kwargs)  # Expect to receive zoom, x, and y in kwargs
        tiles = self._generate_tile(tile)
        return HttpResponse(content=tiles, content_type="application/binary")


class RoadLayerView(TileLayerView):
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
    layers = [MvtQuery(table=OsmAdminBoundary._meta.db_table, attributes=["name"], layer="admin_boundary")]


class IslandsLayerView(TileLayerView):
    layers = [MvtQuery(table=OsmIslands._meta.db_table, attributes=["name"], layer="islands")]


class IslandsAreaLayerView(TileLayerView):
    layers = [MvtQuery(table=OsmIslandsAreas._meta.db_table, attributes=["name"], layer="islands")]


class FacebookAiLayerView(TileLayerView):
    layers = [MvtQuery(table=FacebookAiRoad._meta.db_table, attributes=["highway"], layer="facebookai")]

class BuildingPolygon(TileLayerView):
    layers = [MvtQuery(table="osmflex_buildingpolygon", attributes=["name", "osm_id", "osm_subtype"], layer="buildings", pk="osm_id")]

class MajorRoads(TileLayerView):
    layers = [MvtQuery(table="osmflex_roadmajor", attributes=["name", "osm_type"], layer="roads", pk="osm_id")]

class Hospitals(View):

    def get(self, request, *args, **kwargs):
        model = apps.get_model("osmflex", "AmenityPoint")
        query = model.objects.filter(osm_type__in=["hospital", "clinic"])

        content = serialize('geojson', query,
          geometry_field='geom',
          fields=('name','address', 'osm_type', 'osm_id'))
        return HttpResponse(content=content, content_type="application/json")
