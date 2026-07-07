from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tiles/", include("djangostreetmap.urls", namespace="djangostreetmap")),
]
