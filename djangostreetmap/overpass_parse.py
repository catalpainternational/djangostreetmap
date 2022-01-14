from typing import Dict, List, NamedTuple, Optional, TypeVar, TypedDict, Tuple, Union
import xml.etree.ElementTree as ET
import requests
from django.contrib.gis.geos import Point, LineString
from dataclasses import Field, dataclass
from time import sleep

class Utils:

    @staticmethod
    def tags(el: ET.Element):
        return {tag.attrib['k']: tag.attrib['v'] for tag in el.findall('tag')}

    @staticmethod
    def nodetopoint(node:ET.Element) -> Point:
        return Point(float(node.attrib["lat"]), float(node.attrib["lon"]), srid=4326),

@dataclass
class Query:

    query: bytes
    osm_element: Optional[ET.Element] = None

    # Cached properties
    _nodes: Optional[Dict[int, "Node"]] = None
    _ways: Optional[Dict[int, "Way"]] = None
    _relations: Optional[Dict[int, "Relation"]] = None
    _is_closed: Optional[bool] = None

    def get(self, server = "https://overpass-api.de/api/interpreter"):
        data = dict(data=self.query)
        # This could take some time
        response = requests.post(server, data)
        # Once done
        response.raise_for_status()
        self.osm_element = ET.fromstring(response.content)

    def ensure_element(self):
        while not self.osm_element:
            try:
                self.get()
            except Exception as E:
                sleep(5)

    @property
    def nodes(self) -> Dict[id, "Node"]:
        if self._nodes is not None:
            return self._nodes
        self.ensure_element()
        self._nodes = {n.id: n for n in Node.from_parent_element(self.osm_element)}
        return self._nodes

    @property
    def ways(self) -> Dict[id, "Way"]:
        if self._ways is not None:
            return self._ways
        self.ensure_element()
        self._ways = {way.id: way for way in Way.from_parent_element(self.osm_element)}
        return self._ways

    @property
    def relations(self) -> Dict[int, "Relation"]:
        if self._relations is not None:
            return self._relations
        self.ensure_element()
        self._relations = Relation.from_parent_element(self.osm_element)
        return self._relations

    @property
    def is_closed(self):
        if self._is_closed is not None:
            return self._is_closed
        self._is_closed = self.nodes[0].id == self.nodes[-1].id
        return self.is_closed

@dataclass
class Node:
    id: int
    lat: float
    lon: float
    srid: int = 3246
    tags: Dict[str, str] = None

    _geom: Optional[Point] = None

    @classmethod
    def from_element(cls: "Node", node: ET.Element) -> "Node":
        return cls(
            id = node.attrib['id'],
            lon = node.attrib['lon'],
            lat = node.attrib['lat'],
            tags = Utils.tags(node)
        )
    @classmethod
    def from_parent_element(cls: "Node", parent: ET.Element, tag: str = 'node') -> List["Node"]:
        return [cls.from_element(node) for node in parent.findall(tag)]

    @property
    def geom(self):
        if self._geom is not None:
            return self._geom
        self._geom = Point(self.lat, self.lon, srid=self.srid)


@dataclass
class Nd:
    """
    An "nd" is a reference to a Node
    When called with "out;" as the final clause of the query
    >>> Nd.from_element(ET.fromstring("<nd ref="1797304655"/>))

    When called with "geom out;" as the final clause of the query the node's positional data is embedded
    >>> Nd.from_element(ET.fromstring("<nd ref="1797306059" lat="-8.6032407" lon="125.4985091"/>))
    """

    ref: int
    srid: Optional[int] = 3246  # Typically this is 3246 but may be 3857
    lat: Optional[float] = None
    lon: Optional[float] = None

    _geom: Optional[Point] = None

    @classmethod
    def from_element(cls: "Nd", nd: ET.Element) -> "Nd":
        return cls(
            ref = nd.attrib['ref'],
            # lon and lat may be provided inline or as a reference to another Node
            lon = nd.attrib.get('lon', None),
            lat = nd.attrib.get('lat', None),
        )
    @classmethod
    def from_parent_element(cls: "Nd", parent: ET.Element, tag: str = 'nd') -> List["Nd"]:
        return [cls.from_element(nd) for nd in parent.findall(tag)]

    @property
    def geom(self):
        if self._geom is not None:
            return self._geom
        self._geom = Point(self.lat, self.lon, srid=self.srid)


@dataclass
class Way:

    nodes: List[Node]
    tags: Dict[str, str]

    id: Optional[int] = None

    @property
    def geom(self) -> LineString:
        return LineString(*[node.geom for node in self.nodes])

    @classmethod
    def from_element(cls: "Way", way: ET.Element) -> "Way":
        return Way(
            id = way.attrib['id'],
            nodes = Nd.from_parent_element(way),
            tags = Utils.tags(way),
        )

    @classmethod
    def from_parent_element(cls: "Way", parent: ET.Element, tag: str = 'way') -> List["Way"]:
        return [cls.from_element(node) for node in parent.findall(tag)]

@dataclass
class Member:
    """
    Represents a node or way which is part of a Relation
    """
    type: str  # "node" or "way"
    ref: int  # This is essentially a "foreign key" to a Way or Node
    role: str

    @classmethod
    def from_element(cls, member: ET.Element):
        return cls(
            type=member.attrib["type"],
            ref=int(member.attrib["ref"]),
            role=member.attrib["role"]
        )


@dataclass
class Relation:
    """
    Represents a "relation" tag from overpass
    """
    id: int

    members: List[Union[Way, Node]]
    tags: Dict[str, str]

    @classmethod
    def from_element(cls: "Relation", relation: ET.Element) -> "Relation":
        return Relation(
            id = relation.attrib['id'],
            members = list(Relation.get_members(relation)),
            tags = Utils.tags(relation),
        )

    @classmethod
    def from_parent_element(cls: "Relation", parent: ET.Element, tag: str = 'relation') -> Dict[int, "Relation"]:
        return {rel.id: rel for rel in [cls.from_element(node) for node in parent.findall(tag)]}

    @staticmethod
    def get_members(relation: ET.Element):
        return (Member.from_element(element) for element in relation.iter(tag="member"))

def parse_osm_element(osm: ET.Element) -> List[Node]:
    return [
        Node.from_parent_element(osm),
        Way.from_parent_element(osm)
    ]

def response_to_geometries(query:bytes):

    # Fetch the query from an overpass server
    server = "https://overpass-api.de/api/interpreter"
    data = dict(data=query)
    # This could take some time
    response = requests.post(server, data)
    # Once done
    response.raise_for_status()
    osm_element = ET.fromstring(response.content)

    nodes, ways = parse_osm_element(osm_element)

    return [i for i in nodes]
