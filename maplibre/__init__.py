"""maplibre: pydantic models for the MapLibre style spec.

Tracks the current MapLibre style spec (v25.x). Instantiate
:class:`~maplibre.basemodel.Root` (the top-level style) or any of the layer /
source / light / sky / terrain / projection models directly, or parse an
existing style JSON::

    from maplibre import Root
    style = Root.model_validate_json(open("style.json").read())
"""

from maplibre.basemodel import Root
from maplibre.layer import BackgroundPaint, Layer, Layout, Paint
from maplibre.light import Anchor, Light
from maplibre.projection import Projection
from maplibre.sky import Sky
from maplibre.sources import AnySource, GeoJson, Image, Raster, RasterDem, Source, Vector, Video
from maplibre.sprite import Sprite
from maplibre.terrain import Terrain
from maplibre.transition import Transition

__all__ = [
    "Anchor",
    "AnySource",
    "BackgroundPaint",
    "GeoJson",
    "Image",
    "Layer",
    "Layout",
    "Light",
    "Paint",
    "Projection",
    "Raster",
    "RasterDem",
    "Root",
    "Sky",
    "Source",
    "Sprite",
    "Terrain",
    "Transition",
    "Vector",
    "Video",
]
