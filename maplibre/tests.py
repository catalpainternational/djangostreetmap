from unittest import TestCase

from maplibre import layer

# Create your tests here.
from . import sources


class SourcesTestCase(TestCase):
    def test_vector_tiles(self):
        sources.Vector(**{"tiles": ["http://a.example.com/tiles/{z}/{x}/{y}.pbf", "http://b.example.com/tiles/{z}/{x}/{y}.pbf"], "maxzoom": 14}).json()

    def test_vector_tiles_json(self):
        sources.Vector(url="http://api.example.com/tilejson.json").json()

    def test_vector_mapbox(self):
        sources.Vector(url="mapbox://mapbox.mapbox-streets-v6").json()

    def test_vector_mapboxsatellite(self):
        sources.Vector(url="mapbox://mapbox.satellite", tileSize=256).json()

    def test_raster(self):
        sources.Raster(
            tiles=["http://a.example.com/wms?bbox={bbox-epsg-3857}&format=image/png&service=WMS&version=1.1.1&request=GetMap&srs=EPSG:3857&width=256&height=256&layers=example"],
            tileSize=256,
        ).json()

    def test_rasterdem(self):
        sources.RasterDem(url="mapbox://mapbox.terrain-rgb").json()

    def test_geojson(self):

        sources.GeoJson(
            data={"type": "Feature", "geometry": {"type": "Point", "coordinates": [-77.0323, 38.9131]}, "properties": {"title": "Mapbox DC", "marker-symbol": "monument"}}
        ).json()

    def test_image(self):
        sources.Image(
            url="https://maplibre.org/maplibre-gl-js-docs/assets/radar.gif", coordinates=[[-80.425, 46.437], [-71.516, 46.437], [-71.516, 37.936], [-80.425, 37.936]]
        ).json()

    def test_video(self):
        sources.Video(
            urls=["https://static-assets.mapbox.com/mapbox-gl-js/drone.mp4", "https://static-assets.mapbox.com/mapbox-gl-js/drone.webm"],
            coordinates=[
                [-122.51596391201019, 37.56238816766053],
                [-122.51467645168304, 37.56410183312965],
                [-122.51309394836426, 37.563391708549425],
                [-122.51423120498657, 37.56161849366671],
            ],
        ).json()



class DemoTilesTest(TestCase):
    """
    Reproduce the code at
    https://demotiles.maplibre.org/style.json
    in python files
    """

    @classmethod
    def setUpClass(cls) -> None:

        from importlib import resources
        import json
        cls.style_text = resources.read_text("maplibre", "style.json")
        cls.style = json.loads(cls.style_text)
        return super().setUpClass()

    def test_base(self):
        # Try the entire test file
        ...
        from .basemodel import Root
        root_two = Root.parse_obj(self.style)
        print(root_two)

    def test_demo_backgroundlayer(self):

        # Read the json
        # Try layers...
        layer.LayerFactory(**self.style.get('layers')[0])
