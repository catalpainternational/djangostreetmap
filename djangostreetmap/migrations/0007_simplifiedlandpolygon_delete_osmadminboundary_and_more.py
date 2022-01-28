# Generated by Django 4.0.1 on 2022-01-27 15:56

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangostreetmap", "0006_auto_20211025_2148"),
    ]

    operations = [
        migrations.CreateModel(
            name="SimplifiedLandPolygon",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("geom", django.contrib.gis.db.models.fields.MultiPolygonField(srid=3857)),
            ],
        ),
        migrations.DeleteModel(
            name="OsmAdminBoundary",
        ),
        migrations.DeleteModel(
            name="OsmHighway",
        ),
        migrations.DeleteModel(
            name="OsmIslands",
        ),
        migrations.DeleteModel(
            name="OsmIslandsAreas",
        ),
        migrations.DeleteModel(
            name="PlanetOsmLine",
        ),
        migrations.DeleteModel(
            name="PlanetOsmPoint",
        ),
        migrations.DeleteModel(
            name="PlanetOsmPolygon",
        ),
    ]