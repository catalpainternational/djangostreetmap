import importlib.resources

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from djangostreetmap import scripts


class Command(BaseCommand):
    help = "Set up the machinery to trigger node, way and rel import on XML file content save"

    def add_arguments(self, parser):
        ...

    def handle(self, *args, **options):

        files = [
            "nodes",
            "tags",
            "relations",
            "trigger",
        ]

        with transaction.atomic():
            with connection.cursor() as c:
                for sql_script in files:
                    try:
                        self.stdout.write(self.style.SUCCESS(f"Executing: {sql_script}"))
                        c.execute(importlib.resources.read_text(scripts, f"{sql_script}.sql"))
                    except Exception as E:
                        self.stdout.write(self.style.ERROR(f"Error Executing: {sql_script}"))
                        self.stdout.write(f"{E}")
                        raise
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Done Executing: {sql_script}"))
