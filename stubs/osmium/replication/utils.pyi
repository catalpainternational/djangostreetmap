from typing import Any, NamedTuple

from osmium.osm import NOTHING as NOTHING

LOG: Any

class ReplicationHeader(NamedTuple):
    url: Any
    sequence: Any
    timestamp: Any

def get_replication_header(fname): ...
