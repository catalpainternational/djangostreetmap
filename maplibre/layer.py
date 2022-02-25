"""
A style's layers property lists all the layers available in that style.
The type of layer is specified by the "type" property, and must be one of background,
fill, line, symbol, raster, circle, fill-extrusion, heatmap, hillshade.

Except for layers of the background type, each layer needs to refer to a source. Layers take the data that they get from a source, optionally filter features, and then define how those features are styled.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, validator

Expression = List[Any]
id = str
layout = Dict
Color = str


class TypeEnum(str, Enum):
    fill = "fill"
    line = "line"
    symbol = "symbol"
    circle = "circle"
    heatmap = "heatmap"
    fillExtrusion = "fill-extrusion"
    raster = "raster"
    hillshade = "hillshade"
    background = "background"


class VisibleEnum(str, Enum):
    """
    Layout property. Optional enum.
    One of "visible", "none". Defaults to "visible".
    Whether this layer is displayed."""

    visible = "visible"
    none = "none"


class Paint(Dict[str, Any]):
    ...


class Layout(Dict[str, Any]):
    ...


class BackgroundPaint(BaseModel):
    backgroundColor: Optional[Color] = Field(alias="background-color")
    backgroundOpacity: Optional[int] = Field(alias="background-opacity")
    backgroundPattern: Optional[str] = Field(alias="background-pattern")


class Layer(BaseModel):
    """
    Layers have two sub-properties that determine how data from that layer is rendered: layout and paint properties.
    """

    type: Literal["fill", "line", "symbol", "circle", "heatmap", "fill-extrusion", "raster", "hillshade", "background"]
    filter: Optional[Expression] = Field(
        description="""A expression specifying conditions on source features. Only features that match the filter are displayed. Zoom expressions in filters are only evaluated at integer zoom levels. The feature-state expression is not supported in filter expressions."""
    )
    id: str = Field(description="""Unique layer name.""")
    maxzoom: Optional[int] = Field(
        description="""
        Optional number between 0 and 24 inclusive. The maximum zoom level for the layer. At zoom levels equal to or greater than the maxzoom, the layer will be hidden.
    """
    )
    metadata: Optional[Dict[str, Any]] = Field(
        description="""
        Arbitrary properties useful to track with the layer, but do not influence rendering. Properties should be prefixed to avoid collisions, like 'mapbox:'.
    """
    )
    minzoom: Optional[int] = Field(
        description="""
    The minimum zoom level for the layer. At zoom levels less than the minzoom, the layer will be hidden.
    """
    )
    source: Optional[str] = Field(description="""Name of a source description to be used for this layer. Required for all layer types except background.""")
    sourceLayer: Optional[str] = Field(
        alias="source-layer",
        description="""Layer to use from a vector tile source. Required for vector tile sources; prohibited for all other source types, including GeoJSON sources.""",
    )
    layout: Optional[Layout] = Field(description="Layout propertes for the layer")
    paint: Optional[Paint]

    class Config:
        allow_population_by_field_name = True  # This is true to permit sourceLayer to be set

    @validator("source", allow_reuse=True, always=True)
    def is_background_or_source(cls, v, values):
        if values["type"] == "background":
            return
        if v is not None:
            return v
        raise AssertionError("Layers except 'background' type require a source")
