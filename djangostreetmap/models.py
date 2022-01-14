import gzip
import json
import logging
from typing import Dict, Optional, TypeVar
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.gis.db.models.fields import (
    GeometryField,
    MultiLineStringField,
    MultiPolygonField,
)
from django.contrib.gis.geos import GEOSGeometry
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.utils.text import slugify
from django.utils.timezone import now

from .annotations import GeoJsonFeature, GeoJsonFeatureCollection

T = TypeVar("T")
logger = logging.getLogger(__name__)


class OsmBoundaryManager(models.Manager):
    def create_from_featurecollection(self, featurecollection: GeoJsonFeatureCollection):
        for feature in featurecollection["features"]:
            self.create_from_feature(feature)

    def create_from_feature(self, feature: GeoJsonFeature):
        """
        input_json is a Feature extracted from a GeoJSON request
        """
        osm_id = feature["properties"]["osm_id"]
        geom = GEOSGeometry(json.dumps(feature["geometry"]))
        tags = feature["properties"].pop("all_tags", {})
        meta = feature["properties"]

        self.update_or_create(
            defaults={"osm_id": osm_id},
            geom=geom,
            tags=tags,
            meta=meta,
        )

    def create_from_url(self, url: Optional[str] = None, params: Optional[Dict] = None):

        """
        Download a compressed geoJSON file from osm-boundaries.com
        """

        defaults = dict(
            apiKey=getattr(settings, "BOUNDARIES_API_KEY"),  # Josh's OSM key
            db="osm20211206",  # Replace this with latest value
            osmIds="-305142",  # Replace this with OSM ID of the country to get
            recursive="...",
            format="GeoJSON",
            srid="3857",
            landOnly="...",
            includeAllTags="...",
        )

        # The tags with "..." are key-only
        if url:
            response = requests.get(url)
        else:
            response = requests.get("https://osm-boundaries.com?" + urlencode({**defaults, **(params or {})}).replace("=...", ""))
        response.raise_for_status()
        # Data delivered as GZIP compressed geoJSON

        data_uc = gzip.decompress(response.content)
        json_data = json.loads(data_uc)
        json_data["features"]
        self.create_from_featurecollection(json_data)

    def _load_from_file(self):
        if not self.response:
            raise FileNotFoundError
        self._make_from_overpass_json(json.loads(self.response.read()))


class OsmHighway(models.Model):
    geom = MultiLineStringField(srid=3857)
    name = models.TextField(null=True, blank=True)
    highway = models.TextField()


class OsmAdminBoundary(models.Model):
    geom = MultiLineStringField(srid=3857)
    name = models.TextField(null=True, blank=True)


class OsmIslands(models.Model):
    geom = MultiLineStringField(srid=3857)
    name = models.TextField(null=True, blank=True)


class OsmIslandsAreas(models.Model):
    geom = MultiPolygonField(srid=3857)
    name = models.TextField(null=True, blank=True)


class FacebookAiRoad(models.Model):
    way_fbid = models.BigIntegerField()
    geom = MultiLineStringField(srid=3857)
    highway = models.TextField()


class OverpassManager(models.Manager):

    query = """
        [out:json];
        area["ISO3166-1"="{countrycode}"];
        {node_or_way}[{tag}](area);
        convert item ::=::,::id=id(),::geom=geom(),_osm_type=type();
        out geom;
        """

    def make_queries(self):
        for instance in self.get_queryset():
            if not instance.response:
                print("Fetching %s" % (instance.name,))
                print("Query: %s" % (instance.query,))
                instance.make_query()

    def roads_for_country(self, countrycode: str = "TL"):
        for road_type in [
            "motorway",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
            "unclassified",
            "residential",
            "motorway_link",
            "trunk_link",
            "primary_link",
            "secondary_link",
            "tertiary_link",
            # "living_street"s, "service", "pedestrian", "track", "bus_quideway", "escape", "raceway",
            "road",
            # "busway", "footway", "bridleway", "steps", "corridor", "path"
        ]:
            OverpassQuery.objects.get_or_create(
                name=f"highway={road_type} for {countrycode}", query=self.query.format(countrycode=countrycode, node_or_way="way", tag=f"highway={road_type}")
            )


# Overpass API models
class OverpassQuery(models.Model):
    name = models.CharField(max_length=256)
    query = models.TextField()
    date_fetched = models.DateTimeField(null=True, blank=True)
    response = models.FileField(null=True, blank=True)

    objects = OverpassManager()

    def __str__(self):
        return self.name or self.query

    def make_query(self, url: str = "https://overpass-api.de/api/interpreter"):

        if self.response:
            raise FileExistsError

        logger.info("Requesting: %s", self.query)
        response = requests.post(url=url, data={"data": self.query})
        response.raise_for_status()

        file_name = slugify(self.name or "unknown") + ".json"
        f = ContentFile(
            json.dumps(
                response.json(),
                indent=1,
            )
        )
        self.response.save(file_name, f)
        logger.info("Parsing request JSON")
        self._load_from_file()

    def _load_from_file(self):
        if not self.response:
            raise FileNotFoundError
        self._make_from_overpass_json(json.loads(self.response.read()))

    def _make_from_overpass_json(self, json_content):
        logger.info("Parsing request JSON")
        with transaction.atomic():
            elements = json_content["elements"]
            self.last_fetched = now()
            self.save()
            OverpassResult.objects.filter(query=self).delete()
            for e in elements:
                OverpassResult.objects.from_overpass(e, query=self)


class OverpassResultManager(models.Manager):
    def from_overpass(self, fragment: Dict, query: OverpassQuery) -> "OverpassResult":
        """
        Returns an OverpassResult instance
        from one element returned from overpass
        """
        geometry = GEOSGeometry(json.dumps(fragment["geometry"]).encode())
        tags = fragment["tags"]
        instance = self.update_or_create(defaults={"osm_id": fragment["id"]}, geom=geometry, tags=tags, query=query)[0]
        return instance


class OverpassResult(models.Model):
    """
    Stores features returned from an "overpass" query
    """

    query = models.ForeignKey(OverpassQuery, on_delete=models.CASCADE)
    tags = models.JSONField(null=True)
    geom = GeometryField(srid=3857)
    date_created = models.DateTimeField(auto_now=True)
    osm_id = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.tags.get("name", "")

    objects = OverpassResultManager()


class OsmBoundary(models.Model):
    """
    Data extracted from https://osm-boundaries.com/
    """

    tags = models.JSONField(null=True)
    meta = models.JSONField(null=True)
    geom = GeometryField(srid=3857)
    date_created = models.DateTimeField(auto_now=True)
    osm_id = models.BigIntegerField(null=True, blank=True)

    objects = OsmBoundaryManager()
