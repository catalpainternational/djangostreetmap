"""End-to-end client tests for the tile / GeoJSON / MapStyle views.

Uses the OSM tile coords around Port Moresby for empty-DB smoke tests: the
osmflex tables have no fixtures loaded, so tile responses are zero-length MVT
byte strings. We verify content-type, status, and that MapStyle round-trips
through the pydantic style model.
"""

import json

from django.db import connection
from django.test import TestCase
from django.urls import reverse

from djangostreetmap.tilegenerator import Tile
from djangostreetmap.views import BuildingPolygon, Roads
from maplibre import Root


def _render(composable) -> str:
    """Render a psycopg2 sql.Composable to a string via the live cursor."""
    with connection.cursor() as c:
        return composable.as_string(c.cursor)


class TileEndpointTests(TestCase):
    def test_roads_tile_returns_binary(self):
        url = reverse("djangostreetmap:roads", kwargs={"zoom": 14, "x": 14891, "y": 8624})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/binary")

    def test_buildings_tile_returns_binary(self):
        url = reverse("djangostreetmap:buildings", kwargs={"zoom": 14, "x": 14891, "y": 8624})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/binary")

    def test_land_tile_returns_binary(self):
        url = reverse("djangostreetmap:land", kwargs={"zoom": 14, "x": 14891, "y": 8624})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/binary")

    def test_poi_tile_returns_binary(self):
        url = reverse("djangostreetmap:poi", kwargs={"zoom": 14, "x": 14891, "y": 8624})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)


class BuildingPolygonZoomBandTests(TestCase):
    def test_no_layers_below_zoom_14(self):
        for zoom in (0, 5, 10, 13):
            self.assertEqual(
                BuildingPolygon().get_layers(Tile(zoom=zoom, x=0, y=0)),
                [],
                f"Expected empty layers at zoom {zoom}",
            )

    def test_layers_present_at_zoom_14(self):
        layers = BuildingPolygon().get_layers(Tile(zoom=14, x=0, y=0))
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0].layer, "buildings")


class RoadsZoomBandTests(TestCase):
    def test_low_zoom_filters_out_minor_roads(self):
        """At zoom 3, only classes with min_zoom < 3 (i.e., trunk with min_zoom 2) survive."""
        layers = Roads().get_layers(Tile(zoom=3, x=0, y=0))
        rendered = _render(layers[0].filters[0])
        # `trunk` (min 2) should be in the type filter; `motorway` (min 5) should not.
        self.assertIn("'trunk'", rendered)
        self.assertNotIn("'motorway'", rendered)

    def test_high_zoom_includes_footpaths(self):
        layers = Roads().get_layers(Tile(zoom=14, x=0, y=0))
        rendered = _render(layers[0].filters[0])
        self.assertIn("'footway'", rendered)
        self.assertIn("'residential'", rendered)


class HospitalsAndAerowaysTests(TestCase):
    def test_hospitals_returns_valid_feature_collection(self):
        resp = self.client.get(reverse("djangostreetmap:hospitals"))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertIn("features", data)

    def test_aeroways_returns_valid_feature_collection(self):
        resp = self.client.get(reverse("djangostreetmap:aeroways"))
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["type"], "FeatureCollection")


class MapStyleTests(TestCase):
    def test_style_response_validates_against_root(self):
        resp = self.client.get(reverse("djangostreetmap:map_style"))
        self.assertEqual(resp.status_code, 200)
        payload = json.loads(resp.content)
        # Round-trips through pydantic Root without validation error.
        root = Root.model_validate(payload)
        self.assertEqual(root.version, 8)
        self.assertIn("roads", root.sources)
        self.assertIn("land_polygons", root.sources)
        self.assertIn("poi", root.sources)
        self.assertIn("buildings", root.sources)
