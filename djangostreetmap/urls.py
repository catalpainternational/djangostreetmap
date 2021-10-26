from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (
    AdminBoundaryLayerView,
    ExampleMapView,
    IslandsAreaLayerView,
    RoadLayerView,
)

urlpatterns = [
    path("highways/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(RoadLayerView.as_view())),
    path("admboundary/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(AdminBoundaryLayerView.as_view())),
    path("islands/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(IslandsAreaLayerView.as_view())),
    path("example_map", ExampleMapView.as_view()),
]
