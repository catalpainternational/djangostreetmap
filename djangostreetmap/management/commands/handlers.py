from typing import Iterable

import osmium
from django.contrib.gis.geos import GEOSGeometry, MultiLineString
from django.db.models.query import QuerySet

from djangostreetmap import models


def way_to_linestring(factory, way):
    geom = factory.create_linestring(way)
    geos_geom = GEOSGeometry(geom, srid=4326)
    geos_geom.transform(3857)
    geos_multilinestring = MultiLineString(geos_geom)
    return geos_multilinestring


def gettags(way, *names: Iterable):
    """
    Get only selected tags from a given way
    """
    return {name: way.tags.get(name, None) for name in names}


class HighwayHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.factory = osmium.geom.WKBFactory()
        self.queryset = models.OsmHighway.objects.all()  # type: QuerySet

    def way(self, way: osmium.osm.Way):
        if way.tags.get("highway"):
            self.queryset.filter(id=way.id).delete()
            self.queryset.create(id=way.id, geom=way_to_linestring(self.factory, way), **gettags(way, "name", "highway"))


class OsmAdminBoundaryHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.factory = osmium.geom.WKBFactory()
        self.queryset = models.OsmAdminBoundary.objects.all()  # type: QuerySet

    def way(self, way: osmium.osm.Way):
        if way.tags.get("boundary") == "administrative":

            self.queryset.filter(id=way.id).delete()
            self.queryset.create(id=way.id, geom=way_to_linestring(self.factory, way), **gettags(way, "name"))


class OsmIslandsBoundaryHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.factory = osmium.geom.WKBFactory()
        self.queryset = models.OsmIslands.objects.all()  # type: QuerySet
        self.areas = models.OsmIslandsAreas.objects.all()  # type: QuerySet

    def way(self, way: osmium.osm.Way):
        if way.tags.get("place") == "island":

            self.queryset.filter(id=way.id).delete()
            self.queryset.create(id=way.id, geom=way_to_linestring(self.factory, way), **gettags(way, "name"))

    def area(self, area):
        if area.tags.get("place") == "island":
            self.areas.filter(id=area.id).delete()
            geom = GEOSGeometry(self.factory.create_multipolygon(area), srid=4326)
            geom.transform(3857)
            self.areas.create(id=area.id, geom=geom, **gettags(area, "name"))
