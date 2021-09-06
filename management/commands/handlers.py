import osmium
from django.contrib.gis.geos import GEOSGeometry, MultiLineString
from django.db.models.query import QuerySet

from djangostreetmap import models


class HighwayHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.factory = osmium.geom.WKBFactory()
        self.queryset = models.OsmHighway.objects.all()  # type: QuerySet

    def way(self, way: osmium.osm.Way):
        if way.tags.get("highway"):
            self.queryset.filter(id=way.id).delete()
            self.queryset.create(
                id=way.id, geom=MultiLineString(GEOSGeometry(self.factory.create_linestring(way))), name=way.tags.get("name", None), highway=way.tags.get("highway")
            )


class OsmAdminBoundaryHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.factory = osmium.geom.WKBFactory()
        self.queryset = models.OsmAdminBoundary.objects.all()  # type: QuerySet

    def way(self, way: osmium.osm.Way):
        if way.tags.get("boundary") == "administrative":

            self.queryset.filter(id=way.id).delete()
            self.queryset.create(
                id=way.id,
                geom=MultiLineString(GEOSGeometry(self.factory.create_linestring(way))),
                name=way.tags.get("name", None),
            )


class OsmIslandsBoundaryHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.factory = osmium.geom.WKBFactory()
        self.queryset = models.OsmIslands.objects.all()  # type: QuerySet
        self.areas = models.OsmIslandsAreas.objects.all()  # type: QuerySet

    def way(self, way: osmium.osm.Way):
        if way.tags.get("place") == "island":

            self.queryset.filter(id=way.id).delete()
            self.queryset.create(
                id=way.id,
                geom=MultiLineString(GEOSGeometry(self.factory.create_linestring(way))),
                name=way.tags.get("name", None),
            )

    def area(self, area):
        if area.tags.get("place") == "island":
            self.areas.filter(id=area.id).delete()
            self.areas.create(
                id=area.id,
                geom=GEOSGeometry(self.factory.create_multipolygon(area)),
                name=area.tags.get("name", None),
            )
