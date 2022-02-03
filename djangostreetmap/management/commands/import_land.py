from django.contrib.gis.utils import LayerMapping  # type: ignore
from django.core.management.base import BaseCommand

from djangostreetmap.models import SimplifiedLandPolygon


class Command(BaseCommand):
    help = "Import polygons to the Simplified table"

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="The shp file with the data to import, ie `simplified_land_polygons.shp`")

    def handle(self, *args, **options):
        lm = LayerMapping(SimplifiedLandPolygon, str(options["path"]), mapping=dict(geom="MULTIPOLYGON"), transform=False)
        lm.save(strict=True, verbose=True)
