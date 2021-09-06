from dataclasses import dataclass, field
from typing import List

PgFunction = str


@dataclass
class Tile:
    """
    Simple dataclass representing a "tile" instance and additional metadata
    for tile generation: buffer, extent and margin
    http://postgis.net/docs/ST_TileEnvelope.html

    """

    zoom: int
    x: int
    y: int
    buffer: int = 64
    extent: int = 4096
    margin: str = "(64 / 4096)"

    @property
    def envelope(self) -> str:
        return f"{self.zoom}, {self.x}, {self.y}"

    @property
    def tile_envelope(self) -> PgFunction:
        return f"ST_TileEnvelope({self.envelope})"

    @property
    def tile_envelope_margin(self) -> PgFunction:
        return f"ST_TileEnvelope({self.envelope}, margin => {self.margin})"


@dataclass
class MvtQuery:
    """
    This is a SQL query generator based on the example
    at https://postgis.net/docs/manual-dev/ST_AsMVT.html
    """

    table: str
    attributes: List[str] = field(default_factory=list)
    filters: List[str] = field(default_factory=list)
    srid: int = 3857
    field: str = "geom"
    pk: str = "id"
    layer: str = "default"

    @property
    def json_attributes(self) -> PgFunction:
        """
        Compiles a jsonb_build_object clause from attributes
        Returns a `JSONB_BUILD_OBJECT` function clause
        """
        statements = []
        for attr in self.attributes:
            statements.extend([f"'{attr}'", f'"{attr}"'])
        joined = ", ".join(statements)
        return f" jsonb_build_object({joined}) " if self.attributes else ""

    @property
    def transformed_geom(self) -> PgFunction:
        """
        Return an `ST_TRANSFORM` clause
        https://postgis.net/docs/ST_Transform.html
        """
        return f"ST_TRANSFORM({self.field}, {self.srid})"

    @property
    def alias(self):
        """
        The name of the query alias to use for postgresql
        """
        return f"mvt_{self.layer}"

    def as_mvtgeom(self, tile: Tile) -> PgFunction:
        where = [f"{self.transformed_geom} && {tile.tile_envelope_margin}"]
        where.extend(self.filters)
        where_clause = " AND ".join(where)

        return f"""
        ST_AsMVTGeom(
              {self.transformed_geom},
              {tile.tile_envelope},
              extent => {tile.extent},
              buffer => {tile.buffer}
        ) AS geom, "{self.pk}", {self.json_attributes}
          FROM {self.table}
          WHERE {where_clause}
        """

    def as_mvt(self, tile: Tile) -> PgFunction:
        return f"WITH {self.alias} AS (SELECT {self.as_mvtgeom(tile)}) SELECT ST_AsMVT({self.alias}.*, '{self.layer}', {tile.extent}, 'geom', '{self.pk}') FROM {self.alias}"
