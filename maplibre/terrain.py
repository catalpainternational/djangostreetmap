"""MapLibre style-spec `Terrain` object (3D elevation from a raster-dem source)."""

from pydantic import BaseModel, Field


class Terrain(BaseModel):
    """The `terrain` root-level object binds a raster-dem source to 3D elevation.

    See https://maplibre.org/maplibre-style-spec/terrain/ .
    """

    source: str = Field(description="Name of a raster-dem source in `sources`.")
    exaggeration: float = Field(1.0, ge=0.0, description="Terrain-height exaggeration factor.")
