from django.contrib.gis.gdal.datasource import DataSource
from django.contrib.gis.geos import GEOSGeometry, MultiLineString
from django.core.management.base import BaseCommand

from djangostreetmap.models import FacebookAiRoad


class Command(BaseCommand):
    help = "Import roads from an OSM pbf file"

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="Path to the .gpkg file with the data to import")

    def handle(self, *args, **options):

        ds = DataSource(options["path"])
        for layer in ds:
            for feature in layer:

                geom = MultiLineString(GEOSGeometry(feature.geom.wkb), srid=4326)
                geom.transform(3857)

                FacebookAiRoad.objects.create(
                    geom=geom,
                    way_fbid=int(str(feature["way_fbid"])),
                    highway=feature["highway_tag"],
                )
