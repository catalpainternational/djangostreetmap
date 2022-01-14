from typing import Dict, List, Tuple, TypedDict


class OverpassRequest(TypedDict):
    """
    Represent a POST call to an overpass query
    """

    data: str


class Geometry(TypedDict):
    type: str
    coordinates: List[Tuple[float, float]]


class OverpassElement(TypedDict):
    type: str
    id: int
    geometry: Geometry
    tags: dict


class OverpassResponse(TypedDict):
    """
    Result returned from an overpass query
    """

    version: float
    generator: str
    osm3s: dict
    elements: List[OverpassElement]


class GeoJsonGeometry(TypedDict):
    type: str  # = "name"
    crs: Dict
    coordinates: List[Tuple[float, float]]


class GeoJsonFeature(TypedDict):
    type: str  # "Feature"
    geometry: GeoJsonGeometry
    properties: Dict[str, str]


class GeoJsonFeatureCollection(TypedDict):
    type: str  # "FeatureCollection"
    features: List[GeoJsonFeature]


class OsmBoundariesResponse(TypedDict):
    """
    GeoJSON Response from a query to osm-boundaries.com
    """

    type: str
    features: List[GeoJsonFeature]
