from typing import Any

from pydantic import AnyUrl, BaseModel, Field, ValidationInfo, field_validator

from .layer import Layer
from .light import Light
from .sources import AnySource


class Root(BaseModel):
    id: str | None = None
    bearing: int | float | None = Field(
        None,
        description="""Default bearing, in degrees. The bearing is the compass direction that is "up"; for example, a bearing of 90° orients the map so that east is up. This value will be used only if the map has not been positioned by other means (e.g. map options or user interaction).""",
    )
    center: tuple[float, float] | None = Field(
        None,
        description="""Default map center in longitude and latitude. The style center will be used only if the map has not been positioned by other means (e.g. map options or user interaction).""",
    )
    glyphs: AnyUrl | None = Field(
        None,
        description="""A URL template for loading signed-distance-field glyph sets in PBF format. The URL must include {fontstack} and {range} tokens. This property is required if any layer uses the text-field layout property. The URL must be absolute, containing the scheme, authority and path components.""",
    )
    light: Light | None = Field(None, description="""The global light source.""")
    metadata: dict[str, Any] | None = Field(
        None,
        description="""Arbitrary properties useful to track with the stylesheet, but do not influence rendering. Properties should be prefixed to avoid collisions, like 'mapbox:'.""",
    )
    name: str | None = Field(None, description="""A human-readable name for the style.""")
    pitch: int | float | None = Field(
        None,
        description="""Default pitch, in degrees. Zero is perpendicular to the surface, for a look straight down at the map, while a greater value like 60 looks ahead towards the horizon. The style pitch will be used only if the map has not been positioned by other means (e.g. map options or user interaction).""",
    )
    sources: dict[str, AnySource] = Field(description="""Data source specifications.""")
    layers: list[Layer]
    sprite: AnyUrl | None = Field(
        None,
        description="""A base URL for retrieving the sprite image and metadata. The extensions .png, .json and scale factor @2x.png will be automatically appended. This property is required if any layer uses the background-pattern, fill-pattern, line-pattern, fill-extrusion-pattern, or icon-image properties. The URL must be absolute, containing the scheme, authority and path components.""",
    )
    transition: str | None = Field(
        None,
        description="""A global transition definition to use as a default across properties, to be used for timing transitions between one value and the next when no property-specific transition is set. Collision-based symbol fading is controlled independently of the style's transition property.""",
    )
    version: int = Field(8, description="""Style specification version number.""")

    zoom: float | None = Field(
        None,
        description="""Default zoom level. The style zoom will be used only if the map has not been positioned by other means (e.g. map options or user interaction).""",
    )

    @field_validator("layers")
    @classmethod
    def layer_source_is_in_sources(cls, layers: list[Layer], info: ValidationInfo):
        """
        Ensure that the reference exists in the `sources` map
        """
        sources: dict[str, AnySource] | None = info.data.get("sources")
        if sources is None:
            # sources failed to validate; skip cross-field check
            return layers

        for layer in layers:
            if layer.type == "background":
                continue

            assert layer.source is not None

            source = sources.get(layer.source)

            assert source is not None, "A source-layer is required for vector types: source {} not found for layer {}. Sources are: {}".format(
                layer.source,
                layer.id,
                ", ".join(sources.keys()),
            )

            if source.type == "vector":
                assert layer.sourceLayer is not None, f"A source-layer is required for vector types: no source is specified for layer {layer.id}"
            else:
                assert layer.sourceLayer is None, f"A source-layer is not permitted except for vector types: remove sourceLayer for source {layer.id}"

        return layers
