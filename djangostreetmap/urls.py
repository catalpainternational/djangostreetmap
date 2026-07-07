from django.urls import path
from django.views.decorators.cache import cache_page

from .views import (
    Aeroways,
    BuildingPolygon,
    ExampleMapView,
    Hospitals,
    LandLayer,
    MapStyle,
    PoiLayer,
    Roads,
)

app_name = "djangostreetmap"

urlpatterns = [
    path("example_map", ExampleMapView.as_view()),
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
