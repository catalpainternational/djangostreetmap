from typing import Tuple
from django.test import TestCase
from osmflex.models import RoadLine

from dataclasses import asdict

from djangostreetmap.tilegenerator import MvtQuery, Tile
from psycopg2 import sql

from django.db import connection

# Create your tests here.


class MyTestCase(TestCase):
    def test_foo(self):
        self.assertEqual(True, True)


class RoadMvtTestCase(TestCase):
    def test_roads(self):

        # Specify different zoom levels for road types

        # This reference is from /14/14891/8624, around 'Five Mile', Port Moresby

        port_moresby = Tile(zoom=14, x=14891, y=8624)

        road_osm_types = [
            ("trunk", 2),
            ("steps", 12),
            ("road", 12),
            ("footway", 12),
            ("secondary", 7),
            ("tertiary", 9),
            ("secondary_link", 7),
            ("tertiary_link", 9),
            ("living_street", 12),
            ("pedestrian", 12),
            ("primary", 5),
            ("residential", 13),
            ("primary_link", 5),
            ("track", 12),
            ("motorway_link", 12),
            ("motorway", 5),
            ("service", 12),
            ("unclassified", 12),
            ("path", 12),
        ]  # type: Tuple[Tuple[str, int]]

        # Determine which road types to include in the layer
        road_types = [road_type for road_type, min_zoom in road_osm_types if port_moresby.zoom > min_zoom]

        # Build an array for the query
        type_filter = sql.Identifier("osm_type") + sql.SQL(" = ANY ") + sql.SQL("(ARRAY[")
        type_filter += sql.SQL(",").join([sql.Literal(rt) for rt in road_types])
        type_filter += sql.SQL("]::text[])")

        query = MvtQuery(
            table=RoadLine._meta.db_table,
            attributes=["name", "osm_type"],
            filters=[type_filter],
            layer="transportation",
            transform=False,
            pk="osm_id",
        )

        # These are a query and parameters to pass
        # to a cursor

        with connection.cursor() as cursor:

            # Count the items

            cursor.execute(query.as_mvt(), asdict(port_moresby))

            tile_response = cursor.fetchone()
            content = tile_response[0]  # type: memoryview
        print(bytes(content).decode())


class FromQueryTestCase(TestCase):
    def test_from_query(self):

        port_moresby = Tile(zoom=14, x=14891, y=8624)

        from djangostreetmap.tilegenerator import MvtQuery

        with connection.cursor() as cursor:

            # Count the items

            cursor.execute(MvtQuery.from_model(RoadLine).as_mvt(), asdict(port_moresby))

            tile_response = cursor.fetchone()
            content = tile_response[0]  # type: memoryview
        print(bytes(content).decode())
