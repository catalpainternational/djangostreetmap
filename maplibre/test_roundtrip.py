"""Golden-fixture round-trip tests for the MapLibre style-spec pydantic models.

These load `style.json` and `osm_liberty.json`, validate them via `Root`, and
check that model → JSON → model preserves the essential structure.
"""

import json
from importlib.resources import files
from unittest import TestCase

from maplibre import Layer, Projection, RasterDem, Root, Sky, Terrain, Transition, Vector


def _load(name: str) -> dict:
    return json.loads((files("maplibre") / name).read_text())


class GoldenFixtureRoundtripTests(TestCase):
    def test_style_json_parses(self):
        root = Root.model_validate(_load("style.json"))
        self.assertEqual(root.version, 8)
        self.assertTrue(len(root.layers) > 0)
        self.assertTrue(len(root.sources) > 0)

    def test_osm_liberty_parses(self):
        root = Root.model_validate(_load("osm_liberty.json"))
        self.assertEqual(root.version, 8)
        self.assertTrue(len(root.layers) > 20, "osm_liberty is a rich style with many layers")

    def test_style_json_roundtrips_keys(self):
        original = _load("style.json")
        root = Root.model_validate(original)
        redumped = json.loads(root.model_dump_json(by_alias=True, exclude_unset=True))
        # Sources should survive intact.
        self.assertEqual(set(redumped["sources"]), set(original["sources"]))
        # Every layer id should survive.
        self.assertEqual(
            {layer["id"] for layer in redumped["layers"]},
            {layer["id"] for layer in original["layers"]},
        )


class SpecFieldsTests(TestCase):
    """The newer style-spec top-level fields are wired and typed correctly."""

    def test_transition_is_typed_object(self):
        # `transition` on Root must be the Transition object, not a string.
        root = Root(
            sources={},
            layers=[Layer(id="bg", type="background")],
            transition=Transition(duration=500, delay=100),
        )
        self.assertIsNotNone(root.transition)
        self.assertEqual(root.transition.duration, 500)

    def test_sky_terrain_projection_accepted(self):
        root = Root(
            sources={"dem": RasterDem(url="mapbox://mapbox.terrain-rgb")},
            layers=[Layer(id="bg", type="background")],
            sky=Sky(),
            terrain=Terrain(source="dem", exaggeration=1.5),
            projection=Projection(type="mercator"),
        )
        self.assertEqual(root.terrain.source, "dem")
        self.assertEqual(root.projection.type, "mercator")
        self.assertEqual(root.sky.sky_color, "#88C6FC")

    def test_state_and_roll_and_center_altitude_accepted(self):
        root = Root(
            sources={},
            layers=[Layer(id="bg", type="background")],
            roll=15,
            centerAltitude=1200,
            state={"foo": 42},
        )
        self.assertEqual(root.roll, 15)
        self.assertEqual(root.center_altitude, 1200)
        self.assertEqual(root.state, {"foo": 42})

    def test_color_relief_is_a_valid_layer_type(self):
        layer = Layer(id="relief", type="color-relief", source="dem")
        self.assertEqual(layer.type, "color-relief")

    def test_vector_encoding_field(self):
        v = Vector(tiles=["http://example.com/{z}/{x}/{y}.pbf"], encoding="mlt")
        self.assertEqual(v.encoding.value, "mlt")

    def test_raster_dem_custom_encoding_factors(self):
        rd = RasterDem(
            url="mapbox://foo",
            encoding="custom",
            redFactor=256.0,
            greenFactor=1.0,
            blueFactor=1 / 256.0,
            baseShift=-10000.0,
        )
        self.assertEqual(rd.red_factor, 256.0)
        self.assertAlmostEqual(rd.blue_factor, 1 / 256.0)
        self.assertEqual(rd.base_shift, -10000.0)


class BackgroundLayerValidatorTests(TestCase):
    def test_background_layer_does_not_require_source(self):
        # No `source` kwarg — the field_validator returns None for background type.
        bg = Layer(id="bg", type="background", paint={"background-color": "#fff"})
        self.assertEqual(bg.type, "background")
        self.assertIsNone(bg.source)

    def test_non_background_layer_rejects_explicit_none_source(self):
        # Passing source=None explicitly triggers the field_validator (mode="before"
        # doesn't fire on unset fields — this is by design in pydantic v2).
        with self.assertRaises(Exception) as cm:
            Layer(id="roads", type="line", source=None)
        self.assertIn("background", str(cm.exception).lower())
