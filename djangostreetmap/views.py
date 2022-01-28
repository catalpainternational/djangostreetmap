import logging
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Type, Union

from django.apps import apps
from django.contrib.gis.db.models.functions import Centroid, Transform
from django.db import connection
from django.db.models import Model
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from osmflex.models import OsmLine, OsmPoint, OsmPolygon, RoadLine
from psycopg2 import sql

from djangostreetmap import models
from djangostreetmap.annotations import GeoJsonSerializer, MultiGeoJsonSerializer
from djangostreetmap.functions import AsFeatureCollection, Intersects
from djangostreetmap.tilegenerator import MvtQuery, Tile

from .timer import Timer

logger = logging.getLogger(__name__)


class ExampleMapView(TemplateView):
    template_name = "leaflet_tile_layers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["map_view"] = "[-8.556416, 125.5524171], 14"
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
        return self.layers

    def _generate_tile(self, tile: Tile) -> List[bytes]:

        params = asdict(tile)

        with connection.cursor() as cursor:
            tiles: List[bytes] = []
            for layer in self.get_layers(tile):
                query = layer.as_mvt()
                # Uncomment to see the SQL which is run
                # logger.info(query.as_string(cursor.cursor))
                # with Timer(name="tile generator", logger=logger.info):
                tile_response: Optional[Sequence] = None
                try:
                    cursor.execute(query, params)  # type: ignore
                    tile_response = cursor.fetchone()
                except Exception as E:
                    logger.error(f"{E}")
                    logger.info(query.as_string(cursor.cursor))
                if not tile_response:
                    continue
                content = tile_response[0]
                tiles += content

                if tile_response:
                    content: bytes = tile_response[0]
                    tiles.append(content)

            return tiles

    def get(self, request, *args, **kwargs):
        with Timer(name="tile get", logger=logger.info):
            tile = Tile(**kwargs)  # Expect to receive zoom, x, and y in kwargs
            tiles = b"".join(self._generate_tile(tile))
            return HttpResponse(content=tiles, content_type="application/binary")


class BuildingPolygon(TileLayerView):
    def get_layers(self, tile: Tile):
        if tile.zoom >= 11:
            return [MvtQuery(table="osmflex_buildingpolygon", attributes=["name", "osm_id", "osm_subtype"], layer="buildings", pk="osm_id")]
        elif tile.zoom >= 6:
            return [MvtQuery(table="osmflex_buildingpolygon", attributes=["name", "osm_id", "osm_subtype"], centroid=True, layer="building_point", pk="osm_id")]
        else:
            return []


class MajorRoads(TileLayerView):
    layers = [MvtQuery(table="osmflex_roadmajor", attributes=["name", "osm_type"], layer="roads", pk="osm_id")]


class MinorRoads(TileLayerView):
    def get_layers(self, tile: Tile):
        layers = []
        for road_class, min_zoom in [
            ("trunk", 2),
            ("steps", 12),
            ("road", 12),
            ("footway", 12),
            ("secondary", 7),
            ("tertiary", 9),
            ("secondary_link", 7),
            ("tertiary_link", 9),
            ("living_street", 12),
            ("pedestrian", 12),
            ("primary", 5),
            ("residential", 13),
            ("primary_link", 5),
            ("track", 12),
            ("motorway_link", 12),
            ("motorway", 5),
            ("service", 12),
            ("unclassified", 12),
            ("path", 12),
        ]:
            if tile.zoom > min_zoom:
                layers.append(
                    MvtQuery(
                        table=RoadLine._meta.db_table,
                        attributes=["name", "osm_type"],
                        filters=sql.SQL("{} = {}").format(sql.Identifier("osm_type"), sql.Literal(road_class)),
                        layer=road_class,
                        transform=False,
                        pk="osm_id",
                    )
                )
            else:
                logger.debug("Out of zoom: %s", road_class)

        return layers


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


class LandLayer(TileLayerView):
    layers = [MvtQuery(table=models.SimplifiedLandPolygon._meta.db_table, layer="land")]


class ModelFeatureCollectionView(View):
    """
    Container for OSM layer data
    """

    class Meta:
        proxy = True

    def geojson(
        self,
        model: Union[OsmPoint, OsmLine, OsmPolygon],
        filter_kwargs: Dict[str, Any],
        intersect: Type[Model],  # Note that we make some assumptions about "intersect" model here, see "Intersect" class
        **kwargs,
    ):
        """
        Returns a FeatureCollection of instances from "model" where the geometry
        intersects the area represented by this location profile

        For instance

        >>> OpenStreetMapData.objects.get(area__name="Highlands 1").geojson(AmenityPoint, osm_type="school")
        """
        # The OSM data import is in 3857. We transform to the geom of the
        # surrounding geometry, if applicable
        queryset = model.objects.all().annotate(geom_t=Transform("geom", 4326))
        queryset = queryset.annotate(in_area=Intersects(intersect)).filter(in_area=True)
        queryset = queryset.filter(**filter_kwargs)

        attributes = {field.name: field.name for field in model._meta.fields if field.name != "geom"}
        return queryset.aggregate(_=AsFeatureCollection("geom_t", **attributes))["_"]
