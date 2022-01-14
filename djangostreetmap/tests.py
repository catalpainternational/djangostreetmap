import logging
import os
from functools import cached_property
from pathlib import Path

import requests_mock
from django.test import TestCase

from djangostreetmap import overpass_parse
from djangostreetmap.tilegenerator import MvtQuery, Tile

from .models import OsmBoundary, OverpassQuery

logger = logging.getLogger(__name__)
import xml.etree.ElementTree as ET


class TestJsonImport(TestCase):
    def setUp(self):

        self.url = "https://overpass-api.de/api/interpreter"
        self.file_ = Path(os.path.abspath(__file__)).parent / "pg_health.json"

        self.ql = OverpassQuery(query="""[out:json];area["ISO3166-1"="PG"];node[healthcare](area);convert item ::=::,::geom=geom(),_osm_type=type();out geom;""")
        self.ql.save()

    def test_pg_health_example(self):

        # Test creating Overpass
        with requests_mock.Mocker() as m:
            with open(self.file_, "r") as f:
                m.post(self.url, text=f.read())
            self.ql.make_query()


class TestBoundaryImport(TestCase):
    def setUp(self):
        self.url = "https://osm-boundaries.com/Download/Submit?apiKey=9621eb9d61d9727a2cc47493e8f3e740&db=osm20211206&osmIds=-305142&recursive&format=GeoJSON&srid=4326&landOnly&includeAllTags"
        self.file_ = Path(os.path.abspath(__file__)).parent / "OSMB-72e3130e61dc3b2bad3915658f9b32f1ac1d3bbe.geojson.gz"

    def test_from_url(self):

        with requests_mock.Mocker() as m:
            with open(self.file_, "rb") as f:
                m.get(self.url, content=f.read())
            OsmBoundary.objects.create_from_url(url=self.url)


class TestCompileMvt(TestCase):
    """
    Checks that the MVT tile functions return valid SQL
    """

    def test_table(self):
        q = MvtQuery(table=OsmBoundary._meta.db_table, layer="admin_boundary")
        q.execute(Tile(0, 0, 0))

    def test_model(self):
        q = MvtQuery(model=OsmBoundary, layer="admin_boundary")
        q.execute(Tile(0, 0, 0))

    def test_query(self):
        q = MvtQuery(queryset=OsmBoundary.objects.all(), layer="admin_boundary")
        q.execute(Tile(0, 0, 0))


class TestOverpassParse(TestCase):
    def setUp(self):
        self.node = ET.fromstring('<nd ref="2599693103" lat="-8.5534587" lon="125.5272207"/>')
        self.way = ET.fromstring(
            """
        <way id="24226453">
            <bounds minlat="-8.5535768" minlon="125.5266671" maxlat="-8.5529642" maxlon="125.5272851"/>
            <nd ref="2599693103" lat="-8.5534587" lon="125.5272207"/>
            <nd ref="2599693103" lat="-8.5534587" lon="125.5272207"/>
            <tag k="highway" v="primary"/>
            <tag k="junction" v="roundabout"/>
        </way>
        """
        )
        self.url = "https://overpass-api.de/api/interpreter"
        self.file_ = Path(os.path.abspath(__file__)).parent.parent / "tests" / "rotunda.xml"
        self.query = b"""
            area["ISO3166-1"="TL"]->.Country_area;
            way[highway="primary"][name="Rotunda Nicolau Lobato"](area.Country_area);
            out geom;
            """

        # This has an accent in it
        self.centro_saude = """
            area["ISO3166-1"="TL"]->.Country_area;
            node[healthcare][name="Centtro de Saúde Betano"](area.Country_area);
            out geom;
            """.encode()
        self.file_health_center = Path(os.path.abspath(__file__)).parent.parent / "tests" / "health.xml"

        # This query is for waterways

        self.ww_query = """
        area["ISO3166-1"="TL"]->.Country_area;
        rel[waterway](area.Country_area);
        out geom;
        """
        self.file_relation = Path(os.path.abspath(__file__)).parent.parent / "tests" / "relation.xml"

    def test_geometry_build(self):
        overpass_parse.Utils.nodetopoint(self.node)

    def test_make_nodes(self):
        overpass_parse.Nd.from_element(ET.fromstring('<nd ref="1797304655"/>'))
        overpass_parse.Nd.from_element(ET.fromstring('<nd ref="1797306059" lat="-8.6032407" lon="125.4985091"/>'))

    def test_attribs(self):
        tags = overpass_parse.Utils.tags(self.way)
        self.assertEqual(tags["junction"], "roundabout")
        self.assertEqual(tags["highway"], "primary")

    def test_query(self):
        with requests_mock.Mocker() as m:
            with open(self.file_, "rb") as f:
                m.post(self.url, content=f.read())
            q = overpass_parse.Query(query=self.query)

            self.assertIsNone(q.osm_element)
            q.ensure_element()
            self.assertIsNotNone(q.osm_element)
            ways_one = next(iter(q.ways.items()))[1]
            self.assertEqual(ways_one.tags["junction"], "roundabout")
            self.assertEqual(ways_one.tags["highway"], "primary")

    def test_nodes_query(self):
        with requests_mock.Mocker() as m:
            with open(self.file_health_center, "rb") as f:
                m.post(self.url, content=f.read())
            q = overpass_parse.Query(query=self.centro_saude)

            self.assertIsNone(q.osm_element)
            q.ensure_element()
            self.assertIsNotNone(q.osm_element)
            first_node = next(iter(q.nodes.items()))[1]
            self.assertEqual(first_node.tags["healthcare"], "hospital")

    def test_relations_query(self):
        with requests_mock.Mocker() as m:
            with open(self.file_relation, "rb") as f:
                m.post(self.url, content=f.read())
            q = overpass_parse.Query(query=self.ww_query)

            self.assertIsNone(q.osm_element)

            q.ensure_element()

            q.relations
