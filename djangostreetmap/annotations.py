from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, Sequence, Tuple, Union

from django.db import models

P = Tuple[float, float]
L = Tuple[P]
ML = Tuple[L]

AnyGeom = Union[P, L, ML]


@dataclass
class GeoJsonGeometry:
    type: str  # = "name"
    coordinates: AnyGeom


@dataclass
class GeoJsonFeature:
    type: str  # "Feature"
    geometry: GeoJsonGeometry
    properties: Dict[str, str]


@dataclass
class GeoJsonFeatureCollection:
    type: str  # "FeatureCollection"
    features: List[GeoJsonFeature]


@dataclass
class GeoJsonSerializer:
    queryset: models.QuerySet
    geom_field: str = "geom"
    properties: Optional[Sequence[str]] = None

    def _to_feature(self, feature):
        geom = getattr(feature, self.geom_field)
        _t = geom.geom_type  # type: str
        _c = geom.coords  # type: AnyGeom
        return GeoJsonFeature(
            type="Feature",
            geometry=GeoJsonGeometry(type=_t, coordinates=_c),
            properties={k: getattr(feature, k) for k in self.properties or []},
        )

    def features(self):
        return [self._to_feature(feature) for feature in self.queryset]

    def to_collection(self):
        return GeoJsonFeatureCollection(type="FeatureCollection", features=self.features())


@dataclass
class MultiGeoJsonSerializer:
    serializers: Sequence[GeoJsonSerializer]

    def to_collection(self):

        features = []
        for s in self.serializers:
            features.extend(list(s.features()))

        return GeoJsonFeatureCollection(type="FeatureCollection", features=features)


class TileCache(Protocol):
    """
    Typing protocol for a generic "Cache" method
    The intention of this is to ensure that whichever cache method
    we use for an MvtTile, the cache has at least the methods which
    we access in our code
    """

    def get(self, key, default=None, version=None):
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        pass

    def set(self, key, value, timeout=300, version=None):
        """
        Set a value in the cache. If timeout is given, use that timeout for the
        key; otherwise use the default cache timeout.
        """
        raise NotImplementedError("subclasses of BaseCache must provide a set() method")
