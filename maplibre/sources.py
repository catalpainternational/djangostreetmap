from . import layer
from typing import Dict, List, Literal, Optional, Tuple, Union
from typing_extensions import Annotated
from pydantic import BaseModel, Field, AnyUrl

from enum import Enum
from pydantic import HttpUrl
from djangostreetmap.annotations import GeoJsonFeature, GeoJsonFeatureCollection

"""
Sources state which data the map should display.
Specify the type of source with the "type" property,
which must be one of vector, raster, raster-dem, geojson,
image, video. Adding a source isn't enough to make data
appear on the map because sources don't contain styling
details like color or width. Layers refer to a source
and give it a visual representation. This makes it possible
to style the same source in different ways,
like differentiating between types of roads in
a highways layer.
"""

XY = Tuple[float, float]
Coords = Tuple[XY, XY, XY, XY]


class SchemeEnum(str, Enum):
    xyz = "xyz"  # Slippy map tilenames scheme.
    tms = "tms"  # OSGeo spec scheme.


class EncodingEnum(str, Enum):
    terrarium = "terrarium"
    mapbox = "mapbox"


class Source(BaseModel):
    attribution: Optional[str] = Field(description="Contains an attribution to be displayed when the map is shown to a user.")
    bounds: List[float] = Field(
        [-180, -85.051129, 180, 85.051129],
        description="An array containing the longitude and latitude of the southwest and northeast corners of the source's bounding box in the following order: Field(description="
        ") [sw.lng, sw.lat, ne.lng, ne.lat]. When this property is included in a source, no tiles outside of the given bounds are requested by MapLibre GL.",
    )
    maxzoom: int = Field(
        22,
        description="Maximum zoom level for which tiles are available, as in the TileJSON spec. Data from tiles at the maxzoom are used when displaying the map at higher zoom levels.",
    )
    minzoom: int = Field(0, description="Minimum zoom level for which tiles are available, as in the TileJSON spec.")
    tiles: Optional[List[AnyUrl]] = Field(default_factory=list, description="An array of one or more tile source URLs, as in the TileJSON spec.")
    url: Optional[AnyUrl] = Field(None, description="A URL to a TileJSON resource.")
    volatile: bool = Field(False, description="A setting to determine whether a source's tiles are cached locally.")


class Vector(Source):
    """
    A vector tile source. Tiles must be in Mapbox Vector
    Tile format. All geometric coordinates in vector tiles
    must be between -1 * extent and (extent * 2) - 1 inclusive.
    All layers that use a vector source must specify a
    "source-layer" value. For vector tiles hosted by Mapbox,
    the "url" value should be of the form mapbox://tilesetid.
    """

    type: Literal["vector"] = "vector"
    promoteId: Optional[str] = Field(
        description="""
        A property to use as a feature id (for feature state).
        Either a property name, or an object of the
        form {<sourceLayer>: Field(description="") <propertyName>}.
        If specified as a string for a vector tile source,
        the same property is used across all its source layers."""
    )
    url: Optional[AnyUrl] = Field(None, description="A URL to a TileJSON resource.")
    scheme: SchemeEnum = Field(SchemeEnum.xyz, description="Influences the y direction of the tile coordinates. The global-mercator (aka Spherical Mercator) profile is assumed.")


class Raster(Source):
    type: Literal["raster"] = "raster"
    tileSize: int = Field(512, description="The minimum visual size to display tiles for this layer. Only configurable for raster layers.")


class RasterDem(Source):
    """
    A raster DEM source. Only supports Mapbox Terrain RGB (mapbox://mapbox.terrain-rgb):
    """

    type: Literal["raster-dem"] = "raster-dem"
    encoding: EncodingEnum = Field(EncodingEnum.mapbox, description="The encoding used by this source. Mapbox Terrain RGB is used by default")
    url: Optional[AnyUrl] = Field(None, description="A URL to a TileJSON resource.")


class GeoJson(Source):
    """
    A GeoJSON source. Data must be provided via a "data" property, whose value can be a URL or inline GeoJSON.
    """

    type: Literal["geojson"] = "geojson"
    buffer: int = Field(
        128,
        description="Size of the tile buffer on each side. A value of 0 produces no buffer. A value of 512 produces a buffer as wide as the tile itself. Larger values produce fewer rendering artifacts near tile edges and slower performance.",
    )
    cluster: bool = Field(
        False,
        description="""
    If the data is a collection of point features, setting this to true clusters the points by radius into groups.
    Cluster groups become new Point features in the source with additional properties:
        cluster Is true if the point is a cluster
        cluster_id A unqiue id for the cluster to be used in conjunction with the cluster inspection methods
        point_count Number of original points grouped into this cluster
        point_count_abbreviated An abbreviated point count
    """,
    )
    clusterMaxZoom: Optional[int] = Field(
        description="Max zoom on which to cluster points if clustering is enabled. Defaults to one zoom less than maxzoom (so that last zoom features are not clustered). Clusters are re-evaluated at integer zoom levels so setting clusterMaxZoom to 14 means the clusters will be displayed until z15."
    )
    clusterMinPoints: Optional[int] = Field(2, description="Minimum number of points necessary to form a cluster if clustering is enabled.")
    clusterProperties: Optional[Dict[str, layer.Expression]] = Field(
        description="""
        An object defining custom properties on the generated clusters
        if clustering is enabled, aggregating values from clustered points.
        Has the form {"property_name": [operator, map_expression]}. operator
        is any expression function that accepts at least 2 operands (e.g. "+" or "max") —
        it accumulates the property value from clusters/points the cluster contains;
        map_expression produces the value of a single point.
        Example: {"sum": ["+", ["get", "scalerank"]]}. For more advanced use cases,
        in place of operator, you can use a custom reduce expression that references a
        special ["accumulated"] value,
        e.g.: {"sum": [["+", ["accumulated"], ["get", "sum"]], ["get", "scalerank"]]}
    """
    )
    clusterRadius: int = Field(50, description="Radius of each cluster if clustering is enabled. A value of 512 indicates a radius equal to the width of a tile.")
    data: Union[str, GeoJsonFeature, GeoJsonFeatureCollection] = Field(description="A URL to a GeoJSON file, or inline GeoJSON.")
    filter: Optional[str] = Field(description="An expression for filtering features prior to processing them for rendering.")
    generateId: bool = Field(
        False,
        description="Whether to generate ids for the geojson features. When enabled, the feature.id property will be auto assigned based on its index in the features array, over-writing any previous values.",
    )
    lineMetrics: bool = Field(False, description="Whether to calculate line distance metrics. This is required for line layers that specify line-gradient values.")
    maxzoom: int = Field(18, description="Maximum zoom level at which to create vector tiles (higher means greater detail at high zoom levels).")
    promoteId: Optional[Union[str, Dict[str, str]]] = Field(
        description="A property to use as a feature id (for feature state). Either a property name, or an object of the form {<sourceLayer>: <propertyName>}."
    )
    tolerance: Optional[float] = Field(description="Douglas-Peucker simplification tolerance (higher means simpler geometries and faster performance).")


class Image(BaseModel):
    """
    An image source. The "url" value contains the image location.
    The "coordinates" array contains [longitude, latitude] pairs for the
    image corners listed in clockwise order: top left, top right, bottom right, bottom left.
    """

    type: Literal["image"] = "image"
    coordinates: Coords = Field(description="Corners of image specified in longitude, latitude pairs.")
    url: HttpUrl = Field(description="URL that points to an image.")


class Video(BaseModel):
    """
    An image source. The "url" value contains the image location.
    The "coordinates" array contains [longitude, latitude] pairs for the
    image corners listed in clockwise order: top left, top right, bottom right, bottom left.
    """

    type: Literal["video"] = "video"
    coordinates: Coords = Field(description="Corners of image specified in longitude, latitude pairs.")
    urls: List[HttpUrl] = Field(description="URL that points to an image.")


AnySource = Annotated[Union[Vector, Raster, RasterDem, GeoJson, Image, Video], Field(discriminator="type")]
