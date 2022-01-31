from typing import Any, Dict, List, Optional, Tuple
from typing_extensions import Annotated
from pydantic import BaseModel, HttpUrl, Field
from .sources import AnySource

from .layer import AnyLayer
from .light import Light


class Root(BaseModel):
    bearing: Optional[float] = Field(
        description="""Default bearing, in degrees. The bearing is the compass direction that is "up"; for example, a bearing of 90° orients the map so that east is up. This value will be used only if the map has not been positioned by other means (e.g. map options or user interaction)."""
    )
    center: Optional[Tuple[float, float]] = Field(
        description="""Default map center in longitude and latitude. The style center will be used only if the map has not been positioned by other means (e.g. map options or user interaction)."""
    )
    glyphs: Optional[str] = Field(
        description="""A URL template for loading signed-distance-field glyph sets in PBF format. The URL must include {fontstack} and {range} tokens. This property is required if any layer uses the text-field layout property. The URL must be absolute, containing the scheme, authority and path components."""
    )
    layers: List[Annotated[AnyLayer, Field(discriminator="type", description="""Layers will be drawn in the order of this array.""")]]
    light: Optional[Light] = Field(description="""The global light source.""")
    metadata: Optional[Dict[str, Any]] = Field(
        description="""Arbitrary properties useful to track with the stylesheet, but do not influence rendering. Properties should be prefixed to avoid collisions, like 'mapbox:'."""
    )
    name: Optional[str] = Field(description="""A human-readable name for the style.""")
    pitch: Optional[float] = Field(
        description="""Default pitch, in degrees. Zero is perpendicular to the surface, for a look straight down at the map, while a greater value like 60 looks ahead towards the horizon. The style pitch will be used only if the map has not been positioned by other means (e.g. map options or user interaction).""",
    )
    sources: Dict[str, AnySource] = Field(description="""Data source specifications.""")
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
