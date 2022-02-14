from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Tuple


class Anchor(str, Enum):
    map = "map"
    viewport = "viewport"


class Light(BaseModel):
    anchor: Anchor = Field(Anchor.map, description="""Whether extruded geometries are lit relative to the map or viewport.""")
    color: Optional[str] = Field(description="""Color tint for lighting extruded geometries.""")
    intensity: Optional[float] = Field(description="""Intensity of lighting (on a scale from 0 to 1). Higher numbers will present as more extreme contrast.""")
    position: Optional[Tuple[float, float, float]] = Field(
        (1.15, 210, 30),
        description="""Position of the light source relative to lit (extruded) geometries, in [r radial coordinate, a azimuthal angle, p polar angle] where r indicates the distance from the center of the base of an object to its light, a indicates the position of the light relative to 0° (0° when light.anchor is set to viewport corresponds to the top of the viewport, or 0° when light.anchor is set to map corresponds to due north, and degrees proceed clockwise), and p indicates the height of the light (from 0°, directly above, to 180°, directly below).""",
    )
