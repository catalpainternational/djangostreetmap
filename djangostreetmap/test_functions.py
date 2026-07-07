"""Direct tests for the ORM function wrappers in `djangostreetmap.functions`.

These exercise the SQL generation and query execution against a scratch
`BasicPoint` table without needing populated OSM tables.
"""

from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.geos import Point
from django.db.models import F
from django.test import TestCase

from djangostreetmap.functions import AsFeature, AsFeatureCollection, AsGeoJson, Simplify
from tests.models import BasicPoint


class AsGeoJsonTests(TestCase):
    def test_annotates_point_as_jsonb(self):
        BasicPoint.objects.create(name="p1", geom=Point(1.5, 2.5))
        row = BasicPoint.objects.annotate(g=AsGeoJson("geom")).values("g").get()
        # AsGeoJson output is a JSONB Point.
        self.assertEqual(row["g"]["type"], "Point")
        self.assertAlmostEqual(row["g"]["coordinates"][0], 1.5)
        self.assertAlmostEqual(row["g"]["coordinates"][1], 2.5)


class AsFeatureTests(TestCase):
    def test_feature_shape(self):
        bp = BasicPoint.objects.create(name="p1", geom=Point(3.0, 4.0))
        row = BasicPoint.objects.annotate(f=AsFeature("geom", name=F("name"))).values("f").get()
        self.assertEqual(row["f"]["type"], "Feature")
        self.assertEqual(row["f"]["id"], bp.pk)
        self.assertEqual(row["f"]["geometry"]["type"], "Point")
        self.assertEqual(row["f"]["properties"], {"name": "p1"})


class AsFeatureCollectionTests(TestCase):
    def test_aggregate_multiple_points_into_feature_collection(self):
        BasicPoint.objects.create(name="a", geom=Point(0, 0))
        BasicPoint.objects.create(name="b", geom=Point(1, 1))
        result = BasicPoint.objects.aggregate(fc=AsFeatureCollection("geom", name=F("name")))["fc"]
        self.assertEqual(result["type"], "FeatureCollection")
        self.assertEqual(len(result["features"]), 2)
        names = sorted(f["properties"]["name"] for f in result["features"])
        self.assertEqual(names, ["a", "b"])

    def test_empty_queryset_yields_empty_collection(self):
        result = BasicPoint.objects.aggregate(fc=AsFeatureCollection("geom", name=F("name")))["fc"]
        self.assertEqual(result, {"type": "FeatureCollection", "features": []})


class SimplifyTests(TestCase):
    def test_simplify_survives_query(self):
        """We can round-trip a Simplify() call. Actual tolerance behavior is a PostGIS concern."""
        BasicPoint.objects.create(name="p1", geom=Point(1, 1))
        # Wrap the point in Transform first to give Simplify a projected geometry to chew on.
        row = (
            BasicPoint.objects.annotate(
                g=Simplify(Transform("geom", 3857), tolerance=1.0),
            )
            .values("g")
            .get()
        )
        self.assertIsNotNone(row["g"])
