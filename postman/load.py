import gpxpy
import shapely

import datatypes


def load_gpx(
    filename: str,
) -> tuple[datatypes.TrackCollection, datatypes.NodeCollection]:
    with open(filename) as fp:
        gpx = gpxpy.parse(fp)
    id = 0
    tracks = {}
    for track in gpx.tracks:
        name = track.name.strip("\n")
        print("track", name)
        print(len(track.segments))
        print(track.segments[0].points)
        points = []
        for segment in track.segments:
            for point in segment.points:
                elevation = point.elevation if point.elevation is not None else 0.0
                points.append((point.longitude, point.latitude, elevation))
        print(points)
        tracks[id] = datatypes.Track(name, shapely.LineString(points))
        id += 1
    waypoints = {}
    id = 0
    for waypoint in gpx.waypoints:
        waypoints[id] = datatypes.Node(
            f"{str(id)} {waypoint.name}",
            shapely.Point((waypoint.longitude, waypoint.latitude)),
            [],
        )
        id += 1
    return tracks, waypoints
