from django.contrib import admin
from django.urls import include, path

from tests.views import TestMultiSerializerView, TestSerializerView

app_name = "djangostreetmap"

urlpatterns = [
    path("test_serializer", TestSerializerView.as_view(), name="test_serializer"),
    path("test_multi_serializer", TestMultiSerializerView.as_view(), name="test_multi_serializer"),
    path(
        "",
        include("djangostreetmap.urls", namespace="djangostreetmap"),
    ),
    path("admin/", admin.site.urls),
]
