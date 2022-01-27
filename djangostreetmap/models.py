from django.contrib.gis.db.models.fields import MultiPolygonField
from django.db import models


class SimplifiedLandPolygon(models.Model):
    """
    This is a "simplified polygons" layer from OSM
    """

    geom = MultiPolygonField(srid=3857)
