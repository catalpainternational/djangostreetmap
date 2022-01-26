from django.urls import path
from django.views.decorators.cache import cache_page

from .views import AdminBoundaryLayerView, Aeroways, ExampleMapView, FacebookAiLayerView, Hospitals, IslandsAreaLayerView, MajorRoads, RoadLayerView, BuildingPolygon

app_name = "djangostreetmap"

urlpatterns = [
    path("highways/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(RoadLayerView.as_view()), name="highways"),
    path("admboundary/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(AdminBoundaryLayerView.as_view()), name="admin"),
    path("islands/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(IslandsAreaLayerView.as_view()), name="islands"),
    path("facebookai/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(FacebookAiLayerView.as_view()), name="facebookai"),
    path("example_map", ExampleMapView.as_view()),
    # These allow maps to make reverse URL calls a little easier
    path("highways/", RoadLayerView.as_view(), name="highways"),
    path("admboundary/", AdminBoundaryLayerView.as_view(), name="admin"),
    path("islands/", IslandsAreaLayerView.as_view(), name="islands"),
    path("facebookai/", FacebookAiLayerView.as_view(), name="facebookai"),
    path("buildings/", BuildingPolygon.as_view(), name="buildings"),
    path("buildings/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(BuildingPolygon.as_view()), name="buildings"),
    path("roads/", MajorRoads.as_view(), name="roads"),
    path("roads/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(MajorRoads.as_view()), name="roads"),
    path("hospitals", Hospitals.as_view(), name="hospitals"),
    path("airports", Aeroways.as_view(), name="aeroways"),
]
