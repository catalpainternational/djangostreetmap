"""MapLibre style-spec `Sky` object (root-level sky/atmosphere/fog configuration)."""

from pydantic import BaseModel, ConfigDict, Field


class Sky(BaseModel):
    """The `sky` root-level object controls sky, atmosphere, horizon, and fog rendering.

    See https://maplibre.org/maplibre-style-spec/sky/ .
    """

    model_config = ConfigDict(populate_by_name=True)

    sky_color: str | None = Field("#88C6FC", alias="sky-color", description="Base color for the sky.")
    horizon_color: str | None = Field("#ffffff", alias="horizon-color", description="Base color at the horizon.")
    fog_color: str | None = Field("#ffffff", alias="fog-color", description="Base color for fog; requires 3D terrain.")
    fog_ground_blend: float | None = Field(0.5, alias="fog-ground-blend", description="Blend of fog over 3D terrain from map center to horizon.")
    horizon_fog_blend: float | None = Field(0.8, alias="horizon-fog-blend", description="Blend factor between fog and horizon colors.")
    sky_horizon_blend: float | None = Field(0.8, alias="sky-horizon-blend", description="Blend factor between sky and horizon colors.")
    atmosphere_blend: float | None = Field(0.8, alias="atmosphere-blend", description="Atmosphere visibility; strongest with globe projection.")
