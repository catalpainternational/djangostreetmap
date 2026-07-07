"""MapLibre style-spec `Projection` object."""

from typing import Any

from pydantic import BaseModel, Field


class Projection(BaseModel):
    """The `projection` root-level object selects the map projection.

    In the spec `type` is a "projectionDefinition" — commonly the string
    ``"mercator"`` or ``"vertical-perspective"``, but also an expression (an
    array) for zoom-dependent projection transitions. Modelled as
    ``str | list`` to accept both forms.

    See https://maplibre.org/maplibre-style-spec/projection/ .
    """

    type: str | list[Any] = Field("mercator", description="Projection definition: name string or expression.")
