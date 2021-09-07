from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (
    AdminBoundaryLayerView,
    ExampleMapView,
    IslandsAreaLayerView,
    RoadLayerView,
)

app_name = "djangostreetmap"

urlpatterns = [
    path("highways/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(views.RoadLayerView.as_view()), name="highways"),
    path("admboundary/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(views.AdminBoundaryLayerView.as_view()), name="admin"),
    path("islands/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(views.IslandsAreaLayerView.as_view()), name="islands"),
    path("example_map", views.ExampleMapView.as_view()),
    # These allow maps to make reverse URL calls a little easier
    path("highways/", views.RoadLayerView.as_view(), name="highways"),
    path("admboundary", views.AdminBoundaryLayerView.as_view(), name="admin"),
    path("islands/", views.IslandsAreaLayerView.as_view(), name="islands"),
]
