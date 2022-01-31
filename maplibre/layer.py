"""
A style's layers property lists all the layers available in that style.
The type of layer is specified by the "type" property, and must be one of background,
fill, line, symbol, raster, circle, fill-extrusion, heatmap, hillshade.

Except for layers of the background type, each layer needs to refer to a source. Layers take the data that they get from a source, optionally filter features, and then define how those features are styled.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

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
    backgroundColor: Optional[Color]= Field(alias="background-color")
    backgroundOpacity: Optional[int] = Field(alias="background-opacity")
    backgroundPattern: Optional[str] = Field(alias="background-pattern")

class Layer(BaseModel):
    """
    Layers have two sub-properties that determine how data from that layer is rendered: layout and paint properties.
    """
    filter: Optional[Expression] = Field(description="""A expression specifying conditions on source features. Only features that match the filter are displayed. Zoom expressions in filters are only evaluated at integer zoom levels. The feature-state expression is not supported in filter expressions.""")
    id: str = Field(description = """Unique layer name.""")
    maxzoom: Optional[int] = Field(description = """
        Optional number between 0 and 24 inclusive. The maximum zoom level for the layer. At zoom levels equal to or greater than the maxzoom, the layer will be hidden.
    """)
    metadata: Optional[Dict[str,Any]] = Field(description = """
        Arbitrary properties useful to track with the layer, but do not influence rendering. Properties should be prefixed to avoid collisions, like 'mapbox:'.
    """)
    minzoom: Optional[int] = Field(description = """
    The minimum zoom level for the layer. At zoom levels less than the minzoom, the layer will be hidden.
    """)
    sourceLayer: Optional[str] = Field(alias="source-layer", description="""Layer to use from a vector tile source. Required for vector tile sources; prohibited for all other source types, including GeoJSON sources.""")
    layout: Optional[Layout] = Field(description="Layout propertes for the layer")

class NonBackgroundFill(Layer):
    source: str = Field(description = """Name of a source description to be used for this layer. Required for all layer types except background.""")

class Fill(NonBackgroundFill):
    type: Literal['fill'] = "fill"
    paint: Optional[Paint]


class Line(NonBackgroundFill):
    type: Literal['line'] = "line"
    paint: Optional[Paint]


class Symbol(NonBackgroundFill):
    type: Literal['symbol'] = "symbol"
    paint: Optional[Paint]


class Circle(NonBackgroundFill):
    type: Literal['circle'] = "circle"
    paint: Optional[Paint]


class Heatmap(NonBackgroundFill):
    type: Literal['heatmap'] = "heatmap"
    paint: Optional[Paint]


class FillExtrusion(NonBackgroundFill):
    type: Literal['fill-extrusion'] = "fill-extrusion"
    paint: Optional[Paint]


class Raster(NonBackgroundFill):
    type: Literal['raster'] = "raster"
    paint: Optional[Paint]


class Hillshade(NonBackgroundFill):
    type: Literal['hillshade'] = "hillshade"
    paint: Optional[Paint] = Field()


class Background(Layer):
    type: Literal['background'] = "background"
    paint: Optional[Paint] = Field()


AnyLayer = Union[Fill, Line, Symbol, Circle, Heatmap, FillExtrusion, Raster, Hillshade, Background]
