# boot_django.py
#
# This file sets up and configures Django. It's used by scripts that need to
# execute as if running in a Django server.
import os

import django
from django.conf import settings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "djangostreetmap"))


def boot_django():
    settings.configure(
        BASE_DIR=BASE_DIR,
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.contrib.gis.db.backends.postgis",
                "NAME": "osm",
                "USER": "osm",
                "PASSWORD": "osm",
                "HOST": "localhost",
                "PORT": "49155",
            }
        },
        INSTALLED_APPS=("djangostreetmap",),
        TIME_ZONE="UTC",
        USE_TZ=True,
    )
    django.setup()


if __name__ == "__main__":
    boot_django()
