# Generated by Django 3.1.13 on 2021-09-08 02:14

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangostreetmap", "0005_osmislandsareas"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacebookAiRoad",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("way_fbid", models.IntegerField()),
                ("geom", django.contrib.gis.db.models.fields.MultiLineStringField(srid=3857)),
                ("highway", models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name="PlanetOsmRoads",
        ),
        migrations.AlterField(
            model_name="osmadminboundary",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="osmhighway",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="osmislands",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="osmislandsareas",
            name="id",
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]
