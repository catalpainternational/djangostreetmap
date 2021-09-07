from django.urls import path

from . import views

app_name = "djangostreetmap"

urlpatterns = [
    path("highways/<int:zoom>/<int:x>/<int:y>.pbf", views.RoadLayerView.as_view(), name="highways"),
    path("admboundary/<int:zoom>/<int:x>/<int:y>.pbf", views.AdminBoundaryLayerView.as_view(), name="admin"),
    path("islands/<int:zoom>/<int:x>/<int:y>.pbf", views.IslandsAreaLayerView.as_view(), name="islands"),
    path("example_map", views.ExampleMapView.as_view()),
    # These allow maps to make reverse URL calls a little easier
    path("highways/", views.RoadLayerView.as_view(), name="highways"),
    path("admboundary", views.AdminBoundaryLayerView.as_view(), name="admin"),
    path("islands/", views.IslandsAreaLayerView.as_view(), name="islands"),
]
