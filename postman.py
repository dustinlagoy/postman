import dataclasses

import gpxpy
import shapely

import datatypes
import plot


def load_gpx(filename: str) -> datatypes.TrackCollection:
    with open(filename) as fp:
        gpx = gpxpy.parse(fp)
    id = 0
    tracks = {}
    for track in gpx.tracks:
        name = track.name.strip("\n")
        print("track", name)
        points = []
        for segment in track.segments:
            for point in segment.points:
                points.append((point.longitude, point.latitude, point.elevation))
        tracks[id] = datatypes.Track(name, shapely.LineString(points))
        id += 1
    return tracks


def get_intersections(tracks: datatypes.TrackCollection) -> datatypes.NodeCollection:
    intersections = {}
    node_id = 0
    for id, track in tracks.items():
        for other_id, other_track in tracks.items():
            if id != other_id:
                # TODO check for duplicates
                tmp = track.path.intersection(other_track.path)
                points = None
                if isinstance(tmp, shapely.Point):
                    points = [tmp]
                elif isinstance(tmp, shapely.MultiPoint):
                    points = tmp.geoms
                if points is not None:
                    for item in points:
                        intersections[node_id] = datatypes.Node(
                            track.name + " " + other_track.name,
                            item,
                            {id: track, other_id: other_track},
                        )
                        add_node_to_track(track, node_id, item)
                        add_node_to_track(other_track, node_id, item)
                        node_id += 1
    return intersections


def add_node_to_track(track: datatypes.Track, node_id: int, node_point: shapely.Point):
    if node_point.coords[0] == track.path.coords[0]:
        track.start = node_id
    if node_point.coords[0] == track.path.coords[-1]:
        track.end = node_id
    if (
        node_point.coords[0] != track.path.coords[0]
        and node_point.coords[0] != track.path.coords[-1]
    ):
        track.extra_nodes.append(node_id)


tracks = load_gpx("/home/dustin/nickel-plate-nordic-centre-33365_trails_trailforks.gpx")
nodes = get_intersections(tracks)
for track in tracks.values():
    print(track.name, track.start, track.end, track.extra_nodes)
plot.plot_tracks(tracks, nodes)
