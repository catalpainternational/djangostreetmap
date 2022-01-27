from djangostreetmap import models
from django.contrib.gis import admin


@admin.register(models.SimplifiedLandPolygon)
class SimplifiedLandPolygonAdmin(admin.GISModelAdmin):  # type: ignore
    pass
