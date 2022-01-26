from functools import reduce
from operator import add
from typing import Any, List
from django.apps import apps

from django.db import connection
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.contrib.gis.db.models.functions import Centroid, Transform
from dataclasses import asdict
from psycopg2 import sql

from annotations import GeoJsonSerializer, MultiGeoJsonSerializer

from .models import (
    FacebookAiRoad,
    OsmAdminBoundary,
    OsmHighway,
    OsmIslands,
    OsmIslandsAreas,
)
from .tilegenerator import MvtQuery, Tile


class ExampleMapView(TemplateView):
    template_name = "leaflet_tile_layers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["map_view"] = f"[-8.556416, 125.5524171], 14"
        return context


class TileLayerView(View):
    """
    Handle generation and views of tile layers
    For urls.py you likely want two entries for easier reversing in templates
    >>> path("mylayer/<int:zoom>/<int:x>/<int:y>.pbf", MyTileLayerView.as_view()), name="mylayer"),
    >>> path("mylayer", MyTileLayerView.as_view(), name="mylayer"),
    """

    layers: List[MvtQuery] = []

    def get_layers(self, tile: Tile) -> List[MvtQuery]:
        """
        Override for dynamically determining tile content
        based on tile properties (most likely zoom)
        """

        def filter_for_zoom(layer: MvtQuery):
            if layer.min_render_zoom and tile.zoom < layer.min_render_zoom:
                return False
            if layer.max_render_zoom and tile.zoom > layer.max_render_zoom:
                return False

        return list(filter(filter_for_zoom, self.layers))

    def _generate_tile(self, tile: Tile) -> List[Any]:

        params = asdict(tile)

        with connection.cursor() as cursor:
            tiles = []
            for layer in self.get_layers(tile):
                query = layer.as_mvt()
                cursor.execute(query, params)
                tile_response = cursor.fetchone()
                if tile_response:
                    tiles += tile_response[0]

            return tiles

    def get(self, request, *args, **kwargs):
        tile = Tile(**kwargs)  # Expect to receive zoom, x, and y in kwargs
        tiles = reduce(add, self._generate_tile(tile), b'')
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
                    filters=sql.SQL("{} = {}").format(sql.Identifier("highway"), sql.Literal(road_class)),
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
        AmenityPoint = apps.get_model("osmflex", "AmenityPoint")
        AmenityPolygon = apps.get_model("osmflex", "AmenityPolygon")

        points = AmenityPoint.objects.filter(osm_type__in=["hospital", "clinic"]).annotate(geom_for_json=Transform("geom", 4326))
        centroids = AmenityPolygon.objects.filter(osm_type__in=["hospital", "clinic"]).annotate(geom_centroid=Transform(Centroid("geom"), 4326))

        response = MultiGeoJsonSerializer(
            [
                GeoJsonSerializer(points, "geom_for_json", ("name", "osm_type", "address")),
                GeoJsonSerializer(centroids, "geom_centroid", ("name", "osm_type", "address")),
            ]
        )

        return JsonResponse(data=asdict(response.to_collection()), content_type="application/json")


class Aeroways(View):
    def get(self, request, *args, **kwargs):
        point = apps.get_model("osmflex", "InfrastructurePoint")
        polygon = apps.get_model("osmflex", "InfrastructurePolygon")

        points = point.objects.filter(osm_type__in=["aeroway"]).annotate(geom_for_json=Transform("geom", 4326))
        centroids = polygon.objects.filter(osm_type__in=["aeroway"]).annotate(geom_centroid=Transform(Centroid("geom"), 4326))

        response = MultiGeoJsonSerializer(
            [
                GeoJsonSerializer(points, "geom_for_json", ("name", "osm_type")),
                GeoJsonSerializer(centroids, "geom_centroid", ("name", "osm_type")),
            ]
        )

        return JsonResponse(data=asdict(response.to_collection()), content_type="application/json")
