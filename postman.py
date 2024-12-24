import bisect
import dataclasses
import time

import gpxpy
import shapely

import datatypes
import load
import plot


def get_intersections(tracks: datatypes.TrackCollection) -> datatypes.NodeCollection:
    intersections: datatypes.NodeCollection = {}
    node_id = 0
    start = time.time()
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
                        if is_point_in_nodes(intersections, item):
                            continue
                        print(
                            "adding node {:3d} at intersection of {} and {}".format(
                                node_id, track.name, other_track.name
                            )
                        )
                        intersections[node_id] = datatypes.Node(
                            track.name + " " + other_track.name,
                            item,
                            sorted([id, other_id]),
                        )
                        add_node_to_track(track, node_id, item)
                        add_node_to_track(other_track, node_id, item)
                        node_id += 1
    print("delta", time.time() - start)
    print(f"found {len(intersections)} intersections")
    return intersections


def is_point_in_nodes(nodes: datatypes.NodeCollection, point: shapely.Point) -> bool:
    for id, node in nodes.items():
        if node.point.distance(point) < 0.00001:
            # print(
            #     id,
            #     node.name,
            #     node.point.coords[0],
            #     point.coords[0],
            #     node.point.distance(point),
            # )
            return True
    return False


def add_node_to_track(track: datatypes.Track, node_id: int, node_point: shapely.Point):
    distance = track.path.line_locate_point(node_point, normalized=True)
    last_point = track.path.coords[-1]
    if last_point[:2] == track.path.coords[0][:2]:
        last_point = track.path.coords[-2]
    last_point_distance = track.path.line_locate_point(
        shapely.Point(last_point), normalized=True
    )
    if distance == 0:
        print(f"node {node_id:3d} is start of {track.name}")
        track.start = node_id
    if distance == last_point_distance:
        print(f"node {node_id:3d} is end of {track.name}")
        track.end = node_id
    if distance > 0 and distance < last_point_distance:
        print(f"node {node_id:3d} is {distance*100:.2f}% along {track.name}")
        track.extra_nodes.append(node_id)


def split_tracks(tracks: datatypes.TrackCollection, nodes: datatypes.NodeCollection):
    new_tracks = {}
    new_id = 0
    for id, track in tracks.items():

        def distance(node_id: int):
            return track.path.line_locate_point(nodes[node_id].point)

        track.extra_nodes.sort(key=distance)
        if len(track.extra_nodes) == 0:
            new_tracks[new_id] = track
            new_id += 1
        else:
            new_track = track
            offset_id = 0
            for node_id in track.extra_nodes:
                node = nodes[node_id]
                print()
                print(track.name, node_id, node.name)
                result = split_at_node(new_track, node)
                if result is None:
                    continue
                before, after = result
                print(before.coords[0], before.coords[-1])
                print(after.coords[0], after.coords[-1])
                node.tracks.remove(id)
                new_tracks[new_id] = datatypes.Track(
                    track.name + f" {offset_id}",
                    before,
                    start=new_track.start,
                    end=node_id,
                )
                node.tracks.append(new_id)
                print(id, new_id, node_id, node.tracks)
                new_id += 1
                offset_id += 1
                new_track = datatypes.Track(
                    track.name + f" {offset_id}",
                    after,
                    start=node_id,
                    end=new_track.end,
                )
                node.tracks.append(new_id)
                print(id, new_id, node_id, node.tracks)
            new_tracks[new_id] = new_track
            new_id += 1
    return new_tracks


def split_at_node(
    track: datatypes.Track, node: datatypes.Node
) -> tuple[shapely.LineString, shapely.LineString] | None:
    # shapely.ops.split is unreliable :( so this is a workaround
    distance = track.path.line_locate_point(node.point)

    def track_distance(coords: tuple):
        return track.path.line_locate_point(shapely.Point(coords))

    i_split = bisect.bisect(track.path.coords, distance, key=track_distance)
    if i_split == 0 or i_split == len(track.path.coords):
        return None
    print(i_split, len(track.path.coords))
    print(node.point, track.path.line_locate_point(node.point))
    print(
        track.path.coords[i_split - 1],
        track.path.line_locate_point(shapely.Point(track.path.coords[i_split - 1])),
    )
    print(
        track.path.coords[i_split],
        track.path.line_locate_point(shapely.Point(track.path.coords[i_split])),
    )
    # print(track.path.coords[i_split + 1])
    if node.point == track.path.coords[i_split]:
        before = shapely.LineString(track.path.coords[:i_split])
        after = shapely.LineString(track.path.coords[i_split - 1 :])
    else:
        before = shapely.LineString(track.path.coords[:i_split] + [node.point])
        after = shapely.LineString([node.point] + track.path.coords[i_split:])
    return before, after


tracks = load.load_gpx(
    "/home/dustin/documents/maps/nickel-plate/nickel-plate-nordic-centre-33365_trails_trailforks.gpx"
)
tracks = load.load_gpx("/home/dustin/src/personal/plumber/np.gpx")
nodes = get_intersections(tracks)
for track in tracks.values():
    print(track.name, track.start, track.end, track.extra_nodes)
tracks = split_tracks(tracks, nodes)
plot.plot_tracks(tracks, nodes)
