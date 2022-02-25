from http import HTTPStatus

from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse

from tests.models import BasicPoint


class MyTestCase(TestCase):
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
