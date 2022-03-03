from dataclasses import asdict
from http import HTTPStatus
from typing import List, Tuple

from django.contrib.gis.geos import Point
from django.db import connection
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from osmflex.models import RoadLine
from psycopg2 import sql

from djangostreetmap.tilegenerator import MvtQuery, Tile
from tests.models import BasicPoint

# This reference is from /14/14891/8624, around 'Five Mile', Port Moresby
port_moresby = Tile(zoom=14, x=14891, y=8624)

# Specify different zoom levels for road types
road_osm_types: List[Tuple[str, int]] = [
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
]


class RoadMvtTestCase(TestCase):
    def test_roads_model(self):

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
        with connection.cursor() as cursor:
            cursor.execute(query.as_mvt(), asdict(port_moresby))
            tile_response = cursor.fetchone()
            content = tile_response[0]  # type: memoryview
        return bytes(content)

    def test_roads_queryset(self):

        q = Q()
        for road_type, min_zoom in road_osm_types:
            if port_moresby.zoom >= min_zoom:
                q |= Q(osm_type=road_type)

        queryset = RoadLine.objects.filter(q)
        mvtquery = MvtQuery.from_queryset(queryset)
        params = asdict(port_moresby)
        params.update(mvtquery.query_params)

        with connection.cursor() as cursor:
            cursor.execute(mvtquery.as_mvt(), params)
            tile_response = cursor.fetchone()
            content = tile_response[0]  # type: memoryview
        return bytes(content)


class FromQueryTestCase(TestCase):
    def test_from_query(self):

        with connection.cursor() as cursor:
            cursor.execute(MvtQuery.from_model(RoadLine).as_mvt(), asdict(port_moresby))
            tile_response = cursor.fetchone()
            content = tile_response[0]  # type: memoryview
        return bytes(content)

    def test_from_qs(self):

        queryset = RoadLine.objects.filter(pk__in=[1])
        mvtquery = MvtQuery.from_queryset(queryset)
        params = asdict(port_moresby)
        params.update(mvtquery.query_params)

        with connection.cursor() as cursor:
            cursor.execute(mvtquery.as_mvt(), params)
            tile_response = cursor.fetchone()
            content = tile_response[0]  # type: memoryview
        return bytes(content)


class SerializerTestCase(TestCase):
    def setUp(self) -> None:
        BasicPoint.objects.create(name="Pointy point point", geom=Point(1, 1))
        return super().setUp()

    def test_serialize(self):
        url = reverse("test_serializer")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_multi_serialize(self):
        url = reverse("test_multi_serializer")
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
