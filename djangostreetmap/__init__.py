"""djangostreetmap package.

Compat shim: `osmflex` (<=0.2.3) references `django.contrib.gis.admin.GeoModelAdmin`
and `OSMGeoAdmin`, which were removed in Django 5.0. Alias them to `GISModelAdmin`
so `osmflex.admin` still imports on modern Django. Remove once osmflex ships a fix.
"""

from django.contrib.gis import admin as _gis_admin

if not hasattr(_gis_admin, "GeoModelAdmin"):
    _gis_admin.GeoModelAdmin = _gis_admin.GISModelAdmin  # type: ignore[attr-defined]
if not hasattr(_gis_admin, "OSMGeoAdmin"):
    _gis_admin.OSMGeoAdmin = _gis_admin.GISModelAdmin  # type: ignore[attr-defined]
