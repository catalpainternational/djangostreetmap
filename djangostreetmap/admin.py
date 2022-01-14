from django.contrib.gis import admin

from .models import (
    OsmHighway,
    OsmIslands,
    OverpassQuery,
    OverpassResult,
)
@admin.register(OsmHighway)
class OsmHighwayAdmin(admin.ModelAdmin):
    list_display = ["name", "highway"]


@admin.register(OsmIslands)
class OsmIslandsAdmin(admin.ModelAdmin):
    list_display = ["name"]


class OverpassResultInline(admin.TabularInline):
    model = OverpassResult


@admin.register(OverpassQuery)
class OverpassQueryAdmin(admin.ModelAdmin):
    # inlines = [OverpassResultInline]
    ...


admin.site.register(OverpassResult, admin.OSMGeoAdmin)
