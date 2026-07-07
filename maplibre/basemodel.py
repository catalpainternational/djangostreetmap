"""MapLibre style-spec `Root` object.

Mirrors https://maplibre.org/maplibre-style-spec/root/ .
"""

from typing import Any

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from .layer import Layer
from .light import Light
from .projection import Projection
from .sky import Sky
from .sources import AnySource
from .terrain import Terrain
from .transition import Transition


class Root(BaseModel):
    """Top-level MapLibre style. `sources` and `layers` are the required fields."""

    model_config = ConfigDict(populate_by_name=True)

    version: int = Field(8, description="Style specification version number (must be 8).")
    name: str | None = Field(None, description="A human-readable name for the style.")
    metadata: dict[str, Any] | None = Field(
        None,
        description="Arbitrary properties useful to track with the stylesheet; do not influence rendering. Properties should be prefixed to avoid collisions, like 'mapbox:'.",
    )
    center: tuple[float, float] | None = Field(
        None,
        description="Default map center in [longitude, latitude]. Used only if the map is not otherwise positioned.",
    )
    center_altitude: float | None = Field(
        None,
        alias="centerAltitude",
        description="Default altitude of the map center in meters (v5.0.0+).",
    )
    zoom: float | None = Field(None, description="Default zoom level.")
    bearing: int | float | None = Field(
        None,
        description="Default bearing in degrees. 90° puts east up. Used only if the map is not otherwise positioned.",
    )
    pitch: int | float | None = Field(
        None,
        description="Default pitch in degrees. 0 = looking straight down; higher values tilt toward the horizon.",
    )
    roll: int | float | None = Field(
        None,
        description="Default roll in degrees (v5.0.0+).",
    )
    light: Light | None = Field(None, description="The global light source.")
    sky: Sky | None = Field(None, description="Sky, atmosphere, horizon, and fog configuration.")
    projection: Projection | None = Field(None, description="Map projection.")
    terrain: Terrain | None = Field(None, description="3D terrain configuration referencing a raster-dem source.")
    sources: dict[str, AnySource] = Field(description="Data source specifications.")
    sprite: AnyUrl | list[dict[str, Any]] | None = Field(
        None,
        description=(
            "Sprite atlas: either a base URL (extensions .png/.json/@2x.png appended automatically) or an array of "
            "sprite objects for multi-sprite support. Required if any layer uses a *-pattern or icon-image property."
        ),
    )
    glyphs: AnyUrl | None = Field(
        None,
        description="URL template for signed-distance-field glyph PBFs (must include {fontstack} and {range}).",
    )
    transition: Transition | None = Field(
        None,
        description="Global transition defaults for animated property changes.",
    )
    state: dict[str, Any] | None = Field(
        None,
        description="Style state variables consumable by global-state expressions (v5.6.0+).",
    )
    layers: list[Layer] = Field(description="Ordered list of style layers (bottom-to-top).")

    @field_validator("layers")
    @classmethod
    def layer_source_is_in_sources(cls, layers: list[Layer], info: ValidationInfo):
        """Ensure every non-background layer's `source` references a declared source."""
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
