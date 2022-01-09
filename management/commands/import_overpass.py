from django.core.management.base import BaseCommand

query = """
[out:json];
area["ISO3166-1"="{countrycode}"];
{node_or_way}[{tag}](area);
convert item ::=::,::geom=geom(),_osm_type=type();
out geom;
"""


class Command(BaseCommand):
    help = "Import data from an Overpass server"

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="Path to the .gpkg file with the data to import")

    def handle(self, *args, **options):

        ...
