from typing import Dict, Type

from django.core.management.base import BaseCommand
from osmium import SimpleHandler

from .handlers import HighwayHandler, OsmAdminBoundaryHandler, OsmIslandsBoundaryHandler

handler_layer_map = {
    "highways": HighwayHandler,
    "admin": OsmAdminBoundaryHandler,
    "islands": OsmIslandsBoundaryHandler,
}  # type: Dict[str, Type[SimpleHandler]]


class Command(BaseCommand):
    help = "Import roads from an OSM pbf file"

    def add_arguments(self, parser):
        parser.add_argument("osmfile", type=str, help="Path to the OSM file with the data to import")
        parser.add_argument("layers", type=str, nargs="+", help="Layers to import")

    def handle(self, *args, **options):
        handlers = [handler_layer_map[layer] for layer in options["layers"]]
        for HandlerClass in handlers:  # type: SimpleHandler
            HandlerClass().apply_file(options["osmfile"], locations=True)
