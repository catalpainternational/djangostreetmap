import json
from typing import Dict, List, Tuple, TypedDict, TypeVar

import requests
from django.contrib.gis.db.models.fields import (
    GeometryField,
    MultiLineStringField,
    MultiPolygonField,
)
from django.contrib.gis.geos import GEOSGeometry
from django.db import models, transaction
from django.utils.timezone import now

from .osmimport_models import (  # noqa: F401
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
)

T = TypeVar("T")


class OsmHighway(models.Model):
    geom = MultiLineStringField(srid=3857)
    name = models.TextField(null=True, blank=True)
    highway = models.TextField()


class OsmAdminBoundary(models.Model):
    geom = MultiLineStringField(srid=3857)
    name = models.TextField(null=True, blank=True)


class OsmIslands(models.Model):
    geom = MultiLineStringField(srid=3857)
    name = models.TextField(null=True, blank=True)


class OsmIslandsAreas(models.Model):
    geom = MultiPolygonField(srid=3857)
    name = models.TextField(null=True, blank=True)


class FacebookAiRoad(models.Model):
    way_fbid = models.BigIntegerField()
    geom = MultiLineStringField(srid=3857)
    highway = models.TextField()


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


# Overpass API models
class OverpassQuery(models.Model):
    query = models.TextField()
    date_fetched = models.DateTimeField(null=True)

    def make_query(self, url: str = "https://overpass-api.de/api/interpreter"):
        response = requests.post(url=url, data={"data": self.query})
        response.raise_for_status()
        json_content = response.json()  # type: OverpassResponse
        return self._make_from_overpass_json(json_content)

    def _make_from_overpass_json(self, json_content):
        with transaction.atomic():
            self.save()
            OverpassResult.objects.filter(query=self).delete()
            results = [OverpassResult.from_overpass(e, query=self) for e in json_content["elements"]]
            self.last_fetched = now()
            self.save()
        return results


class OverpassResult(models.Model):
    """
    Stores features returned from an "overpass" query
    """

    query = models.ForeignKey(OverpassQuery, on_delete=models.CASCADE)
    tags = models.JSONField(null=True)
    geom = GeometryField(srid=3857)
    date_created = models.DateTimeField(auto_now=True)

    @classmethod
    def from_overpass(cls, fragment: Dict, query: OverpassQuery) -> "OverpassResult":
        """
        Returns an OverpassResult instance
        from one element returned from overpass
        """
        geometry = GEOSGeometry(json.dumps(fragment["geometry"]).encode())
        tags = fragment["tags"]
        instance = cls(geom=geometry, tags=tags, query=query)
        instance.save()
        return instance
