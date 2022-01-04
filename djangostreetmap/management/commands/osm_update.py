import os

from django.core.management.base import BaseCommand

from djangostreetmap.osm_update import OSMUpdate


class Command(BaseCommand):
    help = "Import roads from an OSM pbf file"

    def add_arguments(self, parser):

        parser.add_argument("region", type=str)
        parser.add_argument("country", type=str)
        parser.add_argument("--cache_dir", type=str)

    def handle(self, *args, **options):

        updater = OSMUpdate(cache_dir=options.get("cache_dir", None), region=options.get("region", "asia"), country=options.get("country", "east-timor"))

        self.stdout.write(self.style.SUCCESS(updater.full_url))
        self.stdout.write(self.style.SUCCESS(updater.get_cache_file))

        if not os.path.exists(updater.get_cache_file):
            self.stdout.write(self.style.SUCCESS("Fetching file"))
            updater.fetch()
        else:
            self.stdout.write(self.style.SUCCESS("Updating file"))
            updater.update_file()
