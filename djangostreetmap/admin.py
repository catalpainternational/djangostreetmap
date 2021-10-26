from django.contrib import admin

from .models import OsmHighway, PlanetOsmLine, PlanetOsmPoint, PlanetOsmPolygon

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


@admin.register(OsmHighway)
class OsmHighwayAdmin(admin.ModelAdmin):
    list_display = ["name", "highway"]
