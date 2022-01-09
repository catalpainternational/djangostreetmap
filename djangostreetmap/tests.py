import logging
import os
from pathlib import Path

import requests
import requests_mock
from django.test import TestCase

from .models import OverpassQuery

logger = logging.getLogger(__name__)


class TestJsonImport(TestCase):
    def setUp(self):
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount("http://", adapter)

        self.session = session
        self.ql = OverpassQuery(query="""[out:json];area["ISO3166-1"="PG"];node[healthcare](area);convert item ::=::,::geom=geom(),_osm_type=type();out geom;""")
        self.ql.save()

    def test_pg_health_example(self):

        # Test creating Overpass
        with requests_mock.Mocker() as m:
            with open(Path(os.path.abspath(__file__)).parent / "pg_health.json", "r") as f:
                m.post("https://overpass-api.de/api/interpreter", text=f.read())
            self.ql.make_query()
