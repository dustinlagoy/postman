import dataclasses

import shapely


@dataclasses.dataclass
class Track:
    name: str
    path: shapely.LineString
    start: int | None = None
    end: int | None = None
    extra_nodes: list[int] = dataclasses.field(default_factory=list)


TrackCollection = dict[int, Track]


@dataclasses.dataclass
class Node:
    name: str
    point: shapely.Point
    tracks: TrackCollection


NodeCollection = dict[int, Node]
