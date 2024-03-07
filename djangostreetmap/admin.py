from django.contrib import admin
from django.contrib.gis.forms import OSMWidget

from djangostreetmap import models


@admin.register(models.SimplifiedLandPolygon)
class SimplifiedLandPolygonAdmin(admin.ModelAdmin):  # type: ignore
    formfield_overrides = {
        models.MultiPolygonField: {"widget": OSMWidget},
    }
