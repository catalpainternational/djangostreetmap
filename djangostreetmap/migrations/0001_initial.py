# Generated by Django 3.1.13 on 2021-09-03 07:14

from typing import List, Tuple

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: List[Tuple[str, str]]

    operations = [
        migrations.CreateModel(
            name="PlanetOsmLine",
            fields=[
                ("unique_id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("osm_id", models.BigIntegerField(blank=True, null=True)),
                ("access", models.CharField(blank=True, max_length=1024, null=True)),
                ("addr_housename", models.CharField(blank=True, db_column="addr:housename", max_length=1024, null=True)),
                ("addr_housenumber", models.CharField(blank=True, db_column="addr:housenumber", max_length=1024, null=True)),
                ("addr_interpolation", models.CharField(blank=True, db_column="addr:interpolation", max_length=1024, null=True)),
                ("admin_level", models.CharField(blank=True, max_length=1024, null=True)),
                ("aerialway", models.CharField(blank=True, max_length=1024, null=True)),
                ("aeroway", models.CharField(blank=True, max_length=1024, null=True)),
                ("amenity", models.CharField(blank=True, max_length=1024, null=True)),
                ("barrier", models.CharField(blank=True, max_length=1024, null=True)),
                ("bicycle", models.CharField(blank=True, max_length=1024, null=True)),
                ("bridge", models.CharField(blank=True, max_length=1024, null=True)),
                ("boundary", models.CharField(blank=True, max_length=1024, null=True)),
                ("building", models.CharField(blank=True, max_length=1024, null=True)),
                ("construction", models.CharField(blank=True, max_length=1024, null=True)),
                ("covered", models.CharField(blank=True, max_length=1024, null=True)),
                ("foot", models.CharField(blank=True, max_length=1024, null=True)),
                ("highway", models.CharField(blank=True, max_length=1024, null=True)),
                ("historic", models.CharField(blank=True, max_length=1024, null=True)),
                ("horse", models.CharField(blank=True, max_length=1024, null=True)),
                ("junction", models.CharField(blank=True, max_length=1024, null=True)),
                ("landuse", models.CharField(blank=True, max_length=1024, null=True)),
                ("layer", models.IntegerField(blank=True, null=True)),
                ("leisure", models.CharField(blank=True, max_length=1024, null=True)),
                ("lock", models.CharField(blank=True, max_length=1024, null=True)),
                ("man_made", models.CharField(blank=True, max_length=1024, null=True)),
                ("military", models.CharField(blank=True, max_length=1024, null=True)),
                ("name", models.CharField(blank=True, max_length=1024, null=True)),
                ("natural", models.CharField(blank=True, max_length=1024, null=True)),
                ("oneway", models.CharField(blank=True, max_length=1024, null=True)),
                ("place", models.CharField(blank=True, max_length=1024, null=True)),
                ("power", models.CharField(blank=True, max_length=1024, null=True)),
                ("railway", models.CharField(blank=True, max_length=1024, null=True)),
                ("ref", models.CharField(blank=True, max_length=1024, null=True)),
                ("religion", models.CharField(blank=True, max_length=1024, null=True)),
                ("route", models.CharField(blank=True, max_length=1024, null=True)),
                ("service", models.CharField(blank=True, max_length=1024, null=True)),
                ("shop", models.CharField(blank=True, max_length=1024, null=True)),
                ("surface", models.CharField(blank=True, max_length=1024, null=True)),
                ("tourism", models.CharField(blank=True, max_length=1024, null=True)),
                ("tracktype", models.CharField(blank=True, max_length=1024, null=True)),
                ("tunnel", models.CharField(blank=True, max_length=1024, null=True)),
                ("water", models.CharField(blank=True, max_length=1024, null=True)),
                ("waterway", models.CharField(blank=True, max_length=1024, null=True)),
                ("way_area", models.FloatField(blank=True, null=True)),
                ("z_order", models.IntegerField(blank=True, null=True)),
                ("way", django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
            ],
            options={
                "db_table": "planet_osm_line",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="PlanetOsmPoint",
            fields=[
                ("unique_id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("osm_id", models.BigIntegerField(blank=True, null=True)),
                ("access", models.CharField(blank=True, max_length=1024, null=True)),
                ("addr_housename", models.CharField(blank=True, db_column="addr:housename", max_length=1024, null=True)),
                ("addr_housenumber", models.CharField(blank=True, db_column="addr:housenumber", max_length=1024, null=True)),
                ("admin_level", models.CharField(blank=True, max_length=1024, null=True)),
                ("aerialway", models.CharField(blank=True, max_length=1024, null=True)),
                ("aeroway", models.CharField(blank=True, max_length=1024, null=True)),
                ("amenity", models.CharField(blank=True, max_length=1024, null=True)),
                ("barrier", models.CharField(blank=True, max_length=1024, null=True)),
                ("boundary", models.CharField(blank=True, max_length=1024, null=True)),
                ("building", models.CharField(blank=True, max_length=1024, null=True)),
                ("highway", models.CharField(blank=True, max_length=1024, null=True)),
                ("historic", models.CharField(blank=True, max_length=1024, null=True)),
                ("junction", models.CharField(blank=True, max_length=1024, null=True)),
                ("landuse", models.CharField(blank=True, max_length=1024, null=True)),
                ("layer", models.IntegerField(blank=True, null=True)),
                ("leisure", models.CharField(blank=True, max_length=1024, null=True)),
                ("lock", models.CharField(blank=True, max_length=1024, null=True)),
                ("man_made", models.CharField(blank=True, max_length=1024, null=True)),
                ("military", models.CharField(blank=True, max_length=1024, null=True)),
                ("name", models.CharField(blank=True, max_length=1024, null=True)),
                ("natural", models.CharField(blank=True, max_length=1024, null=True)),
                ("oneway", models.CharField(blank=True, max_length=1024, null=True)),
                ("place", models.CharField(blank=True, max_length=1024, null=True)),
                ("power", models.CharField(blank=True, max_length=1024, null=True)),
                ("railway", models.CharField(blank=True, max_length=1024, null=True)),
                ("ref", models.CharField(blank=True, max_length=1024, null=True)),
                ("religion", models.CharField(blank=True, max_length=1024, null=True)),
                ("shop", models.CharField(blank=True, max_length=1024, null=True)),
                ("tourism", models.CharField(blank=True, max_length=1024, null=True)),
                ("water", models.CharField(blank=True, max_length=1024, null=True)),
                ("waterway", models.CharField(blank=True, max_length=1024, null=True)),
                ("way", django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
            ],
            options={
                "db_table": "planet_osm_point",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="PlanetOsmPolygon",
            fields=[
                ("unique_id", models.BigIntegerField(primary_key=True, serialize=False)),
                ("osm_id", models.BigIntegerField(blank=True, null=True)),
                ("access", models.CharField(blank=True, max_length=1024, null=True)),
                ("addr_housename", models.CharField(blank=True, db_column="addr:housename", max_length=1024, null=True)),
                ("addr_housenumber", models.CharField(blank=True, db_column="addr:housenumber", max_length=1024, null=True)),
                ("addr_interpolation", models.CharField(blank=True, db_column="addr:interpolation", max_length=1024, null=True)),
                ("admin_level", models.CharField(blank=True, max_length=1024, null=True)),
                ("aerialway", models.CharField(blank=True, max_length=1024, null=True)),
                ("aeroway", models.CharField(blank=True, max_length=1024, null=True)),
                ("amenity", models.CharField(blank=True, max_length=1024, null=True)),
                ("barrier", models.CharField(blank=True, max_length=1024, null=True)),
                ("bicycle", models.CharField(blank=True, max_length=1024, null=True)),
                ("bridge", models.CharField(blank=True, max_length=1024, null=True)),
                ("boundary", models.CharField(blank=True, max_length=1024, null=True)),
                ("building", models.CharField(blank=True, max_length=1024, null=True)),
                ("construction", models.CharField(blank=True, max_length=1024, null=True)),
                ("covered", models.CharField(blank=True, max_length=1024, null=True)),
                ("foot", models.CharField(blank=True, max_length=1024, null=True)),
                ("highway", models.CharField(blank=True, max_length=1024, null=True)),
                ("historic", models.CharField(blank=True, max_length=1024, null=True)),
                ("horse", models.CharField(blank=True, max_length=1024, null=True)),
                ("junction", models.CharField(blank=True, max_length=1024, null=True)),
                ("landuse", models.CharField(blank=True, max_length=1024, null=True)),
                ("layer", models.IntegerField(blank=True, null=True)),
                ("leisure", models.CharField(blank=True, max_length=1024, null=True)),
                ("lock", models.CharField(blank=True, max_length=1024, null=True)),
                ("man_made", models.CharField(blank=True, max_length=1024, null=True)),
                ("military", models.CharField(blank=True, max_length=1024, null=True)),
                ("name", models.CharField(blank=True, max_length=1024, null=True)),
                ("natural", models.CharField(blank=True, max_length=1024, null=True)),
                ("oneway", models.CharField(blank=True, max_length=1024, null=True)),
                ("place", models.CharField(blank=True, max_length=1024, null=True)),
                ("power", models.CharField(blank=True, max_length=1024, null=True)),
                ("railway", models.CharField(blank=True, max_length=1024, null=True)),
                ("ref", models.CharField(blank=True, max_length=1024, null=True)),
                ("religion", models.CharField(blank=True, max_length=1024, null=True)),
                ("route", models.CharField(blank=True, max_length=1024, null=True)),
                ("service", models.CharField(blank=True, max_length=1024, null=True)),
                ("shop", models.CharField(blank=True, max_length=1024, null=True)),
                ("surface", models.CharField(blank=True, max_length=1024, null=True)),
                ("tourism", models.CharField(blank=True, max_length=1024, null=True)),
                ("tracktype", models.CharField(blank=True, max_length=1024, null=True)),
                ("tunnel", models.CharField(blank=True, max_length=1024, null=True)),
                ("water", models.CharField(blank=True, max_length=1024, null=True)),
                ("waterway", models.CharField(blank=True, max_length=1024, null=True)),
                ("way_area", models.FloatField(blank=True, null=True)),
                ("z_order", models.IntegerField(blank=True, null=True)),
                ("way", django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326)),
            ],
            options={
                "db_table": "planet_osm_polygon",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="PlanetOsmRoads",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("djangostreetmap.planetosmline",),
        ),
    ]
