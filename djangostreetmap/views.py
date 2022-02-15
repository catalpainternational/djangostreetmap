import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

from django.apps import apps
from django.contrib.gis.db.models.functions import Centroid, Transform
from django.db import connection
from django.db.models import Model
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.http import HttpRequest
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from osmflex.models import OsmLine, OsmPoint, OsmPolygon, RoadLine, AmenityPoint
from psycopg2 import sql

from djangostreetmap import models
from djangostreetmap.annotations import GeoJsonSerializer, MultiGeoJsonSerializer
from djangostreetmap.functions import AsFeatureCollection, Intersects
from djangostreetmap.tilegenerator import MvtQuery, Tile
from maplibre.basemodel import Root
from maplibre import layer, sources
from maplibre.layer import Layer as L

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
            for query_layer in self.get_layers(tile):
                query = query_layer.as_mvt()
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

            return tiles

    def get(self, request: HttpRequest, *args, **kwargs):
        with Timer(name="tile get", logger=logger.info):
            tile = Tile(**kwargs)  # Expect to receive zoom, x, and y in kwargs
            tiles = b"".join(self._generate_tile(tile))
            return HttpResponse(content=tiles, content_type="application/binary")


class BuildingPolygon(TileLayerView):
    def get_layers(self, tile: Tile):

        if tile.zoom < 14:
            return []

        return [
            MvtQuery(
                table="osmflex_buildingpolygon",
                attributes=["name", "osm_id", "osm_subtype"],
                calculated_attributes={"render_min_height": sql.SQL('COALESCE("height", "levels" * 4, 4)')},
                layer="buildings",
                pk="osm_id",
            )
        ]


class Roads(TileLayerView):
    def get_layers(self, tile: Tile):

        road_osm_types = [
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
        ]  # type: List[Tuple[str, int]]

        # Determine which road types to include in the layer

        type_filter = sql.SQL("""{field} = ANY(ARRAY[{types}]::text[])""").format(
            field=sql.Identifier("osm_type"), types=sql.SQL(",").join([sql.Literal(rt) for rt, mz in road_osm_types if tile.zoom > mz])
        )

        roads = MvtQuery(
            table=RoadLine._meta.db_table,
            attributes=["name", "osm_type"],
            filters=[type_filter],
            layer="transportation",
            transform=False,
            pk="osm_id",
        )

        return [roads]


class Hospitals(View):
    def get(self, request: HttpRequest, *args, **kwargs):
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
    def get(self, request: HttpRequest, *args, **kwargs):
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


class PoiLayer(TileLayerView):
    layers = [
        MvtQuery(
            table=AmenityPoint._meta.db_table,
            attributes=["name"],
            # filters = sql.SQL("{} = {}").format(sql.Identifier("osm_type"), sql.Literal("school")),
            layer="school",
            pk="osm_id",
        )
    ]


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


class MapStyle(View):
    """
    Return a simple "mapbox"
    JSON view
    """

    def get(self, request: HttpRequest, *args, **kwargs):

        # map = Root()
        road_source = sources.Vector(type="vector", tiles=[f"{request.scheme}://{request.get_host()}{reverse('djangostreetmap:roads')}{{z}}/{{x}}/{{y}}.pbf"])
        land_source = sources.Vector(type="vector", tiles=[f"{request.scheme}://{request.get_host()}{reverse('djangostreetmap:land')}{{z}}/{{x}}/{{y}}.pbf"])
        poi_source = sources.Vector(type="vector", tiles=[f"{request.scheme}://{request.get_host()}{reverse('djangostreetmap:poi')}{{z}}/{{x}}/{{y}}.pbf"])
        building_source = sources.Vector(type="vector", tiles=[f"{request.scheme}://{request.get_host()}{reverse('djangostreetmap:buildings')}{{z}}/{{x}}/{{y}}.pbf"])

        background = layer.Layer(id="background", type="background", paint={"background-color": "rgb(158,189,255)"})

        # Styles for every kind of road

        # Set the line, source and layout which are common properties of all roads
        road_common = {"type": "line", "source": "roads", "sourceLayer": "transportation", "layout": {"line-join": "round", "line-cap": "round"}}

        road_casing = [
            L(
                id="road_trunk_casing",
                filter=["all", ["==", "osm_type", "trunk"]],
                paint={"line-color": "#e9ac77", "line-width": {"base": 1.2, "stops": [[5, 0.4], [6, 0.7], [7, 1.75], [20, 22]]}},
                **road_common,
            ),
            L(
                id="road_primary_casing",
                filter=["all", ["==", "osm_type", "primary"]],
                paint={"line-color": "#e9ac77", "line-width": {"base": 1.2, "stops": [[5, 0.4], [6, 0.7], [7, 1.75], [20, 22]]}},
                **road_common,
            ),
            L(
                id="road_secondary_casing",
                filter=["all", ["==", "osm_type", "secondary"]],
                paint={"line-color": "#e9ac77", "line-width": {"base": 1.2, "stops": [[8, 1.5], [20, 17]]}},
                **road_common,
            ),
            L(
                id="road_tertiary_casing",
                filter=["all", ["==", "osm_type", "tertiary"]],
                paint={"line-color": "#e9ac77", "line-width": {"base": 1.2, "stops": [[8, 1.5], [20, 17]]}},
                **road_common,
            ),
            L(
                id="road_motorway_casing",
                filter=["all", ["==", "osm_type", "motorway"]],
                paint={"line-color": "#e9ac77", "line-width": {"base": 1.2, "stops": [[5, 0.4], [6, 0.7], [7, 1.75], [20, 22]]}},
                **road_common,
            ),
            L(
                id="road_residential_casing",
                filter=["all", ["==", "osm_type", "residential"]],
                paint={"line-color": "#cfcdca", "line-opacity": {"stops": [[12, 0], [12.5, 1]]}, "line-width": {"base": 1.2, "stops": [[12, 0.5], [13, 1], [14, 4], [20, 20]]}},
                **road_common,
            ),
            L(
                id="road_service_casing",
                filter=["all", ["==", "osm_type", "service"]],
                paint={"line-color": "#cfcdca", "line-width": {"base": 1.2, "stops": [[15, 1], [16, 4], [20, 11]]}},
                **road_common,
            ),
        ]

        # Road inner
        road_lines = [
            L(
                id="road_motorway",
                filter=["all", ["==", "osm_type", "motorway"]],
                paint={"line-color": {"base": 1, "stops": [[5, "hsl(26, 87%, 62%)"], [6, "#fc8"]]}, "line-width": {"base": 1.2, "stops": [[5, 0], [7, 1], [20, 18]]}},
                **road_common,
            ),
            L(
                id="road_trunk",
                filter=["all", ["==", "osm_type", "trunk"]],
                paint={"line-color": "#fea", "line-width": {"base": 1.2, "stops": [[5, 0], [7, 1], [20, 18]]}},
                **road_common,
            ),
            L(
                id="road_residential",
                filter=["all", ["==", "osm_type", "residential"]],
                paint={"line-color": "#fff", "line-width": {"base": 1.2, "stops": [[13.5, 0], [14, 2.5], [20, 18]]}},
                **road_common,
            ),
            L(
                id="road_service",
                filter=["all", ["==", "osm_type", "service"]],
                paint={"line-color": "#fff", "line-width": {"base": 1.2, "stops": [[13.5, 0], [14, 2.5], [20, 18]]}},
                **road_common,
            ),
            L(
                id="road_primary",
                filter=["all", ["==", "osm_type", "primary"]],
                paint={"line-color": "#fea", "line-width": {"base": 1.2, "stops": [[5, 0], [7, 1], [20, 18]]}},
                **road_common,
            ),
            L(
                id="road_secondary",
                filter=["all", ["==", "osm_type", "secondary"]],
                paint={"line-color": "#fea", "line-width": {"base": 1.2, "stops": [[6.5, 0], [8, 0.5], [20, 13]]}},
                **road_common,
            ),
            L(
                id="road_tertiary",
                filter=["all", ["==", "osm_type", "tertiary"]],
                paint={"line-color": "#fea", "line-width": {"base": 1.2, "stops": [[6.5, 0], [8, 0.5], [20, 13]]}},
                **road_common,
            ),
        ]

        # Road labels
        road_labels = [
            layer.Layer(
                id="road_highway_label",
                type="symbol",
                source="roads",
                sourceLayer="transportation",
                filter=["all", ["==", "osm_type", "highway"]],
                layout={
                    "symbol-placement": "line",
                    "text-anchor": "center",
                    "text-field": "{name}",
                    "text-font": ["Roboto Regular"],
                    "text-offset": [0, 0.15],
                    "text-size": {"base": 1, "stops": [[13, 12], [14, 13]]},
                },
                paint={"text-color": "#765", "text-halo-blur": 0.5, "text-halo-width": 1},
            ),
            layer.Layer(
                id="road_trunk_label",
                type="symbol",
                source="roads",
                sourceLayer="transportation",
                filter=["all", ["==", "osm_type", "trunk"]],
                layout={
                    "symbol-placement": "line",
                    "text-anchor": "center",
                    "text-field": "{name}",
                    "text-font": ["Roboto Regular"],
                    "text-offset": [0, 0.15],
                    "text-size": {"base": 1, "stops": [[13, 12], [14, 13]]},
                },
                paint={"text-color": "#765", "text-halo-blur": 0.5, "text-halo-width": 1},
            ),
            layer.Layer(
                id="road_primary_label",
                type="symbol",
                source="roads",
                sourceLayer="transportation",
                filter=["all", ["==", "osm_type", "primary"]],
                layout={
                    "symbol-placement": "line",
                    "text-anchor": "center",
                    "text-field": "{name}",
                    "text-font": ["Roboto Regular"],
                    "text-offset": [0, 0.15],
                    "text-size": {"base": 1, "stops": [[13, 12], [14, 13]]},
                },
                paint={"text-color": "#765", "text-halo-blur": 0.5, "text-halo-width": 1},
            ),
            layer.Layer(
                id="road_secondary_label",
                type="symbol",
                source="roads",
                sourceLayer="transportation",
                filter=["all", ["==", "osm_type", "secondary"]],
                layout={
                    "symbol-placement": "line",
                    "text-anchor": "center",
                    "text-field": "{name}",
                    "text-font": ["Roboto Regular"],
                    "text-offset": [0, 0.15],
                    "text-size": {"base": 1, "stops": [[13, 12], [14, 13]]},
                },
                paint={"text-color": "#765", "text-halo-blur": 0.5, "text-halo-width": 1},
            ),
            layer.Layer(
                id="road_tertiary_label",
                type="symbol",
                source="roads",
                sourceLayer="transportation",
                filter=["all", ["==", "osm_type", "tertiary"]],
                layout={
                    "symbol-placement": "line",
                    "text-anchor": "center",
                    "text-field": "{name}",
                    "text-font": ["Roboto Regular"],
                    "text-offset": [0, 0.15],
                    "text-size": {"base": 1, "stops": [[13, 12], [14, 13]]},
                },
                paint={"text-color": "#765", "text-halo-blur": 0.5, "text-halo-width": 1},
            ),
            layer.Layer(
                id="road_residential_label",
                type="symbol",
                source="roads",
                sourceLayer="transportation",
                filter=["all", ["==", "osm_type", "residential"]],
                layout={
                    "symbol-placement": "line",
                    "text-anchor": "center",
                    "text-field": "{name}",
                    "text-font": ["Roboto Regular"],
                    "text-offset": [0, 0.15],
                    "text-size": {"base": 1, "stops": [[13, 12], [14, 13]]},
                },
                paint={"text-color": "#765", "text-halo-blur": 0.5, "text-halo-width": 1},
            ),
            layer.Layer(
                id="road_service_label",
                type="symbol",
                source="roads",
                sourceLayer="transportation",
                filter=["all", ["==", "osm_type", "service"]],
                layout={
                    "symbol-placement": "line",
                    "text-anchor": "center",
                    "text-field": "{name}",
                    "text-font": ["Roboto Regular"],
                    "text-offset": [0, 0.15],
                    "text-size": {"base": 1, "stops": [[13, 12], [14, 13]]},
                },
                paint={"text-color": "#765", "text-halo-blur": 0.5, "text-halo-width": 1},
            ),
        ]

        # POI (Points Of Interest)
        poi_layers = [
            layer.Layer(
                id="poi_school",
                type="symbol",
                source="poi",
                sourceLayer="school",
                layout={
                    "icon-image": "school_11",
                    "text-anchor": "top",
                    "text-field": "{name}",
                    "text-font": ["Roboto Condensed Italic"],
                    "text-max-width": 9,
                    "text-offset": [0, 0.6],
                    "text-size": 12,
                },
                paint={"text-color": "#666", "text-halo-blur": 0.5, "text-halo-color": "#ffffff", "text-halo-width": 1},
            )
        ]

        buildings = [
            layer.Layer(
                **{
                    "id": "building-3d",
                    "type": "fill-extrusion",
                    "source": "buildings",
                    "sourceLayer": "buildings",
                    "minzoom": 14,
                    "paint": {
                        "fill-extrusion-color": "hsl(35, 8%, 85%)",
                        "fill-extrusion-height": {"property": "render_min_height", "type": "identity"},
                        "fill-extrusion-opacity": 0.8,
                    },
                }
            )
        ]

        land_layer = layer.Layer(type="fill", id="land", source="land_polygons", sourceLayer="land", paint={"fill-color": "rgb(239,239,239)"})

        map = Root(
            sprite="https://maputnik.github.io/osm-liberty/sprites/osm-liberty",
            glyphs="https://api.maptiler.com/fonts/{fontstack}/{range}.pbf?key={key}",
            version=8,
            sources={
                "roads": road_source,
                "land_polygons": land_source,
                "poi": poi_source,
                "buildings": building_source,
            },
            layers=[background, land_layer, *road_casing, *road_lines, *road_labels, *poi_layers, *buildings],
        )

        return HttpResponse(map.json(exclude_unset=True, by_alias=True), content_type="application/json")
