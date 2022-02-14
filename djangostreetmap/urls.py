from django.urls import path
from django.views.decorators.cache import cache_page

from .views import Aeroways, BuildingPolygon, ExampleMapView, Hospitals, LandLayer, Roads, MapStyle, PoiLayer

app_name = "djangostreetmap"

urlpatterns = [
    # path("highways/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(RoadLayerView.as_view()), name="highways"),
    # path("admboundary/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(AdminBoundaryLayerView.as_view()), name="admin"),
    # path("islands/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(IslandsAreaLayerView.as_view()), name="islands"),
    # path("facebookai/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(FacebookAiLayerView.as_view()), name="facebookai"),
    path("example_map", ExampleMapView.as_view()),
    # These allow maps to make reverse URL calls a little easier
    # path("highways/", RoadLayerView.as_view(), name="highways"),
    # path("admboundary/", AdminBoundaryLayerView.as_view(), name="admin"),
    # path("islands/", IslandsAreaLayerView.as_view(), name="islands"),
    # path("facebookai/", FacebookAiLayerView.as_view(), name="facebookai"),
    path("buildings/", BuildingPolygon.as_view(), name="buildings"),
    path("buildings/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(BuildingPolygon.as_view()), name="buildings"),
    path("roads/", Roads.as_view(), name="roads"),
    path("roads/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(Roads.as_view()), name="roads"),
    path("hospitals", Hospitals.as_view(), name="hospitals"),
    path("airports", Aeroways.as_view(), name="aeroways"),
    path("land/", cache_page(60 * 15)(LandLayer.as_view()), name="land"),
    path("land/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(LandLayer.as_view()), name="land"),
    path("poi/", cache_page(60 * 15)(PoiLayer.as_view()), name="poi"),
    path("poi/<int:zoom>/<int:x>/<int:y>.pbf", cache_page(60 * 15)(PoiLayer.as_view()), name="poi"),
    path("style", MapStyle.as_view(), name="map_style"),
]
