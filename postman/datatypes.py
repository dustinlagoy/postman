import dataclasses
import typing

import shapely

Tour = list[tuple[float, float, dict[str, typing.Any]]]


@dataclasses.dataclass
class Track:
    name: str
    id: int
    path: shapely.LineString


TrackCollection = dict[int, Track]
