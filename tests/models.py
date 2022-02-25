from django.contrib.gis.db.models import PointField
from django.db import models


class BasicPoint(models.Model):
    name = models.TextField()
    geom = PointField(srid=4326)
