# Generated by Django 3.2.7 on 2021-09-06 04:53

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangostreetmap", "0004_osmislands"),
    ]

    operations = [
        migrations.CreateModel(
            name="OsmIslandsAreas",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("geom", django.contrib.gis.db.models.fields.MultiPolygonField(srid=3857)),
                ("name", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
