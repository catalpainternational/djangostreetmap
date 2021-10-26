from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (
    AdminBoundaryLayerView,
    ExampleMapView,
    FacebookAiLayerView,
    IslandsAreaLayerView,
    RoadLayerView,
)

app_name = "djangostreetmap"

urlpatterns = [
    path("highways/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(RoadLayerView.as_view()), name="highways"),
    path("admboundary/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(AdminBoundaryLayerView.as_view()), name="admin"),
    path("islands/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(IslandsAreaLayerView.as_view()), name="islands"),
    path("facebookai/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(FacebookAiLayerView.as_view()), name="islands"),
    path("example_map", ExampleMapView.as_view()),
    # These allow maps to make reverse URL calls a little easier
    path("highways/", RoadLayerView.as_view(), name="highways"),
    path("admboundary/", AdminBoundaryLayerView.as_view(), name="admin"),
    path("islands/", IslandsAreaLayerView.as_view(), name="islands"),
    path("facebookai/", FacebookAiLayerView.as_view(), name="facebookai"),
]
