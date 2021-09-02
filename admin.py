from django.contrib import admin
from .models import PlanetOsmLine, PlanetOsmPoint, PlanetOsmPolygon,PlanetOsmRoads
# Register your models here.

@admin.register(PlanetOsmLine)
class PlanetOsmLineAdmin(admin.ModelAdmin):
    ...

@admin.register(PlanetOsmPoint)
class PlanetOsmPointAdmin(admin.ModelAdmin):
    ...

@admin.register(PlanetOsmPolygon)
class PlanetOsmPolygonAdmin(admin.ModelAdmin):
    ...

@admin.register(PlanetOsmRoads)
class PlanetOsmRoadsAdmin(admin.ModelAdmin):
    ...
