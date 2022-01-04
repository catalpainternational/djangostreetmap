from django.contrib import admin
from django.urls import include, path

app_name = "djangostreetmap"

urlpatterns = [
    path(
        "",
        include("djangostreetmap.urls", namespace="djangostreetmap"),
    ),
    path("admin/", admin.site.urls),
]
