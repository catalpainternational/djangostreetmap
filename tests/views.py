from dataclasses import asdict

from django.http import JsonResponse
from django.views import View

from djangostreetmap.annotations import GeoJsonSerializer, MultiGeoJsonSerializer
from tests.models import BasicPoint


class TestMultiSerializerView(View):
    def get(self, request, *args, **kwargs):
        response = MultiGeoJsonSerializer(
            [
                GeoJsonSerializer(BasicPoint.objects.all(), "geom", ("name",)),
                GeoJsonSerializer(BasicPoint.objects.all(), "geom", ("name",)),
            ]
        )

        return JsonResponse(data=asdict(response.to_collection()), content_type="application/json")


class TestSerializerView(View):
    def get(self, request, *args, **kwargs):
        response = GeoJsonSerializer(BasicPoint.objects.all(), "geom", ("name",))
        return JsonResponse(data=asdict(response.to_collection()), content_type="application/json")
