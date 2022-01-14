from django.contrib.gis import admin

from .models import (
    OsmAdminBoundary,
    OsmHighway,
    OsmIslands,
    OverpassQuery,
    OverpassResult,
)

# Register your models here.


# @admin.register(PlanetOsmLine)
# class PlanetOsmLineAdmin(admin.ModelAdmin):
#     list_display = ["name", "boundary", "highway", "waterway"]


# @admin.register(PlanetOsmPoint)
# class PlanetOsmPointAdmin(admin.ModelAdmin):
#     list_display = ["name", "place", "amenity", "natural"]


# @admin.register(PlanetOsmPolygon)
# class PlanetOsmPolygonAdmin(admin.ModelAdmin):
#     list_display = ["name", "place"]


@admin.register(OsmHighway)
class OsmHighwayAdmin(admin.ModelAdmin):
    list_display = ["name", "highway"]


@admin.register(OsmIslands)
class OsmIslandsAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(OsmAdminBoundary)
class OsmAdminBoundaryAdmin(admin.ModelAdmin):
    list_display = ["name"]


class OverpassResultInline(admin.TabularInline):
    model = OverpassResult


@admin.register(OverpassQuery)
class OverpassQueryAdmin(admin.ModelAdmin):
    # inlines = [OverpassResultInline]
    ...


admin.site.register(OverpassResult, admin.OSMGeoAdmin)
