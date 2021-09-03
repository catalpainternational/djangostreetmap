from django.contrib import admin

from .models import PlanetOsmLine, PlanetOsmPoint, PlanetOsmPolygon, PlanetOsmRoads

# Register your models here.


@admin.register(PlanetOsmLine)
class PlanetOsmLineAdmin(admin.ModelAdmin):
    list_display = ["name", "boundary", "highway", "waterway"]


@admin.register(PlanetOsmPoint)
class PlanetOsmPointAdmin(admin.ModelAdmin):
    list_display = ["name", "place", "amenity", "natural"]


@admin.register(PlanetOsmPolygon)
class PlanetOsmPolygonAdmin(admin.ModelAdmin):
    list_display = ["name", "place"]


@admin.register(PlanetOsmRoads)
class PlanetOsmRoadsAdmin(admin.ModelAdmin):
    list_display = ["name", "boundary", "highway", "waterway"]
