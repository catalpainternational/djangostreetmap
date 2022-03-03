import docker
from django.conf import settings
from django.core.management.base import BaseCommand

client = docker.from_env()


class Command(BaseCommand):
    help = "Run a test postgis container on a given port"

    def handle(self, *args, **options):

        client.containers.run(
            "postgis/postgis:14-3.2",
            "-c fsync=off",
            auto_remove=True,
            ports={"4326/tcp": settings.DATABASES["default"]["PORT"]},
            name="djangostreetmap",
            environment={"POSTGRES_PASSWORD": settings.DATABASES["default"]["PASSWORD"]},
        )
