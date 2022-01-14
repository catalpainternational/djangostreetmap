from django.core.management.base import BaseCommand

from djangostreetmap.models import OverpassQuery


class Command(BaseCommand):
    help = "Import data from an Overpass server"

    def add_arguments(self, parser):
        parser.add_argument("tag", type=str, help="Tags to import (eg 'highway')")
        parser.add_argument("countrycode", type=str, help="ISO code for the country to import")
        parser.add_argument("node_or_way", type=str, help="Use way for lines , node for nodes, nwr for everything")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Start importing "))
        q = OverpassQuery(query=OverpassQuery.objects.query.format(**options))
        q.make_query()
