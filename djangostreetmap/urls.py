from django.contrib import admin
from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (
    AdminBoundaryView,
    ExampleMapView,
    FacebookAiLayerView,
    IslandsAreaLayerView,
    OverpassJSONView,
    OverpassView,
    RoadLayerView,
)

app_name = "djangostreetmap"

urlpatterns = [
    path("highways/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(RoadLayerView.as_view()), name="highways"),
    path("islands/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(IslandsAreaLayerView.as_view()), name="islands"),
    path("facebookai/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(FacebookAiLayerView.as_view()), name="islands"),
    path("overpass/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(OverpassView.as_view()), name="overpass"),
    path("boundary/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(AdminBoundaryView.as_view()), name="boundary"),
    path("example_map", ExampleMapView.as_view()),
    # These allow maps to make reverse URL calls a little easier
    path("highways/", RoadLayerView.as_view(), name="highways"),
    path("islands/", IslandsAreaLayerView.as_view(), name="islands"),
    path("facebookai/", FacebookAiLayerView.as_view(), name="facebookai"),
    path("overpass/", OverpassView.as_view(), name="overpass"),
    path("overpassjson/", OverpassJSONView.as_view(), name="overpassjson"),
    path("boundary/", AdminBoundaryView.as_view(), name="boundary"),
    path("admin/", admin.site.urls),
]
