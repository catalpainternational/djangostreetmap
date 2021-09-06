from django.core.management.base import BaseCommand

from .handlers import HighwayHandler, OsmAdminBoundaryHandler, OsmIslandsBoundaryHandler


class Command(BaseCommand):
    help = "Import roads from an OSM pbf file"

    def add_arguments(self, parser):
        parser.add_argument("osmfile", type=str, help="Path to the OSM file with the data to import")

    def handle(self, *args, **options):
        HighwayHandler().apply_file(options["osmfile"], locations=True)
        OsmAdminBoundaryHandler().apply_file(options["osmfile"], locations=True)
        OsmIslandsBoundaryHandler().apply_file(options["osmfile"], locations=True)
