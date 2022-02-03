from django.contrib.gis import admin

from djangostreetmap import models


@admin.register(models.SimplifiedLandPolygon)
class SimplifiedLandPolygonAdmin(admin.GeoModelAdmin):  # type: ignore
    pass
