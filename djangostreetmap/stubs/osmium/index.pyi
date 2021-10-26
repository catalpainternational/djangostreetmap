import osmium.osm._osm

class LocationTable:
    def __init__(self, *args, **kwargs) -> None: ...
    def clear(self) -> None: ...
    def get(self, id: int) -> osmium.osm._osm.Location: ...
    def set(self, id: int, loc: osmium.osm._osm.Location) -> None: ...
    def used_memory(self) -> int: ...

def create_map(map_type: str) -> LocationTable: ...
def map_types() -> list: ...