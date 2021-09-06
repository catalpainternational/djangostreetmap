from typing import Any

class OSMObject:
    id: Any
    version: Any
    visible: Any
    changeset: Any
    timestamp: Any
    uid: Any
    tags: Any
    user: Any
    def __init__(
        self,
        base: Any | None = ...,
        id: Any | None = ...,
        version: Any | None = ...,
        visible: Any | None = ...,
        changeset: Any | None = ...,
        timestamp: Any | None = ...,
        uid: Any | None = ...,
        tags: Any | None = ...,
        user: Any | None = ...,
    ) -> None: ...

class Node(OSMObject):
    location: Any
    def __init__(self, base: Any | None = ..., location: Any | None = ..., **attrs) -> None: ...

class Way(OSMObject):
    nodes: Any
    def __init__(self, base: Any | None = ..., nodes: Any | None = ..., **attrs) -> None: ...

class Relation(OSMObject):
    members: Any
    def __init__(self, base: Any | None = ..., members: Any | None = ..., **attrs) -> None: ...
