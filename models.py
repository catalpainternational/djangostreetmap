from django.contrib.gis.db.models.fields import MultiLineStringField, MultiPolygonField
from django.db import models

from .osmimport_models import (  # noqa: F401
    PlanetOsmLine,
    PlanetOsmPoint,
    PlanetOsmPolygon,
)


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
