"""
A style's layers property lists all the layers available in that style.
The type of layer is specified by the "type" property, and must be one of background,
fill, line, symbol, raster, circle, fill-extrusion, heatmap, hillshade.

Except for layers of the background type, each layer needs to refer to a source. Layers take the data that they get from a source, optionally filter features, and then define how those features are styled.
"""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

Expression = list[Any]
id = str
Color = str
Paint = dict[str, Any]
Layout = dict[str, Any]


class TypeEnum(str, Enum):
    fill = "fill"
    line = "line"
    symbol = "symbol"
    circle = "circle"
    heatmap = "heatmap"
    fillExtrusion = "fill-extrusion"
    raster = "raster"
    hillshade = "hillshade"
    colorRelief = "color-relief"
    background = "background"


class VisibleEnum(str, Enum):
    """
    Layout property. Optional enum.
    One of "visible", "none". Defaults to "visible".
    Whether this layer is displayed."""

    visible = "visible"
    none = "none"


class BackgroundPaint(BaseModel):
    backgroundColor: Color | None = Field(None, alias="background-color")
    backgroundOpacity: int | None = Field(None, alias="background-opacity")
    backgroundPattern: str | None = Field(None, alias="background-pattern")


class Layer(BaseModel):
    """
    Layers have two sub-properties that determine how data from that layer is rendered: layout and paint properties.
    """

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["fill", "line", "symbol", "circle", "heatmap", "fill-extrusion", "raster", "hillshade", "color-relief", "background"]
    filter: Expression | None = Field(
        None,
        description="""A expression specifying conditions on source features. Only features that match the filter are displayed. Zoom expressions in filters are only evaluated at integer zoom levels. The feature-state expression is not supported in filter expressions.""",
    )
    id: str = Field(description="""Unique layer name.""")
    maxzoom: int | None = Field(
        None,
        description="""
        Optional number between 0 and 24 inclusive. The maximum zoom level for the layer. At zoom levels equal to or greater than the maxzoom, the layer will be hidden.
    """,
    )
    metadata: dict[str, Any] | None = Field(
        None,
        description="""
        Arbitrary properties useful to track with the layer, but do not influence rendering. Properties should be prefixed to avoid collisions, like 'mapbox:'.
    """,
    )
    minzoom: int | None = Field(
        None,
        description="""
    The minimum zoom level for the layer. At zoom levels less than the minzoom, the layer will be hidden.
    """,
    )
    source: str | None = Field(None, description="""Name of a source description to be used for this layer. Required for all layer types except background.""")
    sourceLayer: str | None = Field(
        None,
        alias="source-layer",
        description="""Layer to use from a vector tile source. Required for vector tile sources; prohibited for all other source types, including GeoJSON sources.""",
    )
    layout: Layout | None = Field(None, description="Layout propertes for the layer")
    paint: Paint | None = None

    @field_validator("source", mode="before")
    @classmethod
    def is_background_or_source(cls, v, info: ValidationInfo):
        if info.data.get("type") == "background":
            return None
        if v is not None:
            return v
        raise AssertionError("Layers except 'background' type require a source")
