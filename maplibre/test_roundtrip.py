"""Golden-fixture round-trip tests for the MapLibre style-spec pydantic models.

These load `style.json` and `osm_liberty.json`, validate them via `Root`, and
check that model → JSON → model preserves the essential structure.
"""

import json
from importlib.resources import files
from unittest import TestCase

from maplibre import Layer, Root


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
