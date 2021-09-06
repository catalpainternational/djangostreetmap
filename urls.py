from django.urls import path

from . import views

urlpatterns = [
    path("highways/<int:zoom>/<int:x>/<int:y>.pbf", views.RoadLayerView.as_view()),
    path("admboundary/<int:zoom>/<int:x>/<int:y>.pbf", views.AdminBoundaryLayerView.as_view()),
    path("islands/<int:zoom>/<int:x>/<int:y>.pbf", views.IslandsAreaLayerView.as_view()),
    path("example_map", views.ExampleMapView.as_view()),
]
