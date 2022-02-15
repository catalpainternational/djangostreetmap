from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated
from pydantic import BaseModel, HttpUrl, Field, validator
from .sources import AnySource

from .layer import Layer
from .light import Light


class Root(BaseModel):
    id: Optional[str]
    bearing: Optional[Union[int, float]] = Field(
        description="""Default bearing, in degrees. The bearing is the compass direction that is "up"; for example, a bearing of 90° orients the map so that east is up. This value will be used only if the map has not been positioned by other means (e.g. map options or user interaction)."""
    )
    center: Optional[Tuple[float, float]] = Field(
        description="""Default map center in longitude and latitude. The style center will be used only if the map has not been positioned by other means (e.g. map options or user interaction)."""
    )
    glyphs: Optional[str] = Field(
        description="""A URL template for loading signed-distance-field glyph sets in PBF format. The URL must include {fontstack} and {range} tokens. This property is required if any layer uses the text-field layout property. The URL must be absolute, containing the scheme, authority and path components."""
    )
    light: Optional[Light] = Field(description="""The global light source.""")
    metadata: Optional[Dict[str, Any]] = Field(
        description="""Arbitrary properties useful to track with the stylesheet, but do not influence rendering. Properties should be prefixed to avoid collisions, like 'mapbox:'."""
    )
    name: Optional[str] = Field(description="""A human-readable name for the style.""")
    pitch: Optional[Union[int, float]] = Field(
        description="""Default pitch, in degrees. Zero is perpendicular to the surface, for a look straight down at the map, while a greater value like 60 looks ahead towards the horizon. The style pitch will be used only if the map has not been positioned by other means (e.g. map options or user interaction).""",
    )
    sources: Dict[str, AnySource] = Field(description="""Data source specifications.""")
    layers: List[Annotated[Layer, Field(description="""Layers will be drawn in the order of this array.""")]]
    sprite: Optional[HttpUrl] = Field(
        description="""A base URL for retrieving the sprite image and metadata. The extensions .png, .json and scale factor @2x.png will be automatically appended. This property is required if any layer uses the background-pattern, fill-pattern, line-pattern, fill-extrusion-pattern, or icon-image properties. The URL must be absolute, containing the scheme, authority and path components."""
    )
    transition: Optional[str] = Field(
        description="""A global transition definition to use as a default across properties, to be used for timing transitions between one value and the next when no property-specific transition is set. Collision-based symbol fading is controlled independently of the style's transition property."""
    )
    version: int = Field(8, description="""Style specification version number.""")

    zoom: Optional[float] = Field(
        description="""Default zoom level. The style zoom will be used only if the map has not been positioned by other means (e.g. map options or user interaction)."""
    )

    @validator("layers", allow_reuse=True)
    def layer_source_is_in_sources(cls, layers: List[Layer], values):
        """
        Ensure that the reference exists in the `sources` map
        """

        sources = values["sources"]  # type: Dict[str, AnySource]

        for layer in layers:

            if layer.type == "background":
                continue

            assert layer.source is not None

            source = sources.get(layer.source)

            assert source is not None, "A source-layer is required for vector types: source %s not found for layer %s. Sources are: %s" % (
                layer.source,
                layer.id,
                ", ".join(sources.keys()),
            )

            if source.type == "vector":
                assert layer.sourceLayer is not None, "A source-layer is required for vector types: no source is specified for layer %s" % (layer.id,)

            else:
                assert layer.sourceLayer is None, "A source-layer is not permitted except for vector types: remove sourceLayer for source %s" % (layer.id,)

        return layers
