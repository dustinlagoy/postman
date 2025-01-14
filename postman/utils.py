import networkx as nx
import pyproj
import shapely

from postman import datatypes, srtm


def _id(x):
    id = x.get("index_position", None)
    if id is None:
        id = x.name
    return id


def _name(x):
    return str(x["name"]).strip()


def label(x: dict):
    return "{:03d} {}".format(_id(x), _name(x))


def label_len(x):
    return "{:03d} {:8.2f} {}".format(_id(x), x["geometry"].length, _name(x))


def label_len_header():
    return "id  distance name"


def rearrange(tour: datatypes.TrackCollection, ids: list[tuple[int, int]]):
    ids = [
        (62, 39),
        (63, 62),
        (88, 61),
        (0, 88),
        (1, 0),
        (2, 1),
        (89, 2),
    ]
    ids = [
        (65, 46),
        (66, 65),
        (91, 64),
        (0, 91),
        (1, 0),
        (2, 1),
        (92, 2),
    ]
    tmp = list(tour.values())
    for from_id, to_id in ids:
        item = tour[from_id]
        tmp.pop(tmp.index(item))
        to_index = tmp.index(tour[to_id])
        print(
            "move {} {} to {} {}".format(
                from_id, item.name, to_index, tmp[to_index].name
            )
        )
        tmp.insert(to_index + 1, item)
    out = {}
    for i, item in enumerate(tmp):
        out[i] = item
        item.id = i
    return out


def print_tour(tour: datatypes.Tour):
    length = 0
    total_up = 0
    total_down = 0
    print(f"num       up     down {label_len_header()}")
    for i, (_, _, data) in enumerate(tour):
        up = data["elevation_gain"]
        down = data["elevation_loss"]
        print("{:3d} {:8.2f} {:8.2f} {}".format(i, up, down, label_len(data)))
        length += data["distance"]
        total_up += up
        total_down += down
    print(
        "total distance {:10.2f} up {:8.2f} down {:8.2f}".format(
            length, total_up, total_down
        )
    )


def print_trails(trails):
    print(f"num   distance name")
    for i in trails.iterrows():
        print(
            "{:3d} {:10.2f} {}".format(
                i[0], i[1]["distance"], str(i[1]["name"]).strip()
            )
        )
    print(
        "total distance {:10.2f}".format(sum(x.distance for _, x in trails.iterrows()))
    )


def print_graph_by_edges(graph: nx.MultiGraph):
    for i, (u, v, data) in enumerate(graph.edges(data=True)):
        print("edge between nodes {:4d} and {:4d} is {}".format(u, v, label_len(data)))
        # print(
        #     "{:02d} {:12.4f} {}".format(i, data["distance"], str(data["name"]).strip())
        # )
    print(
        "total distance {:10.2f}".format(
            sum(x["distance"] for _, _, x in graph.edges(data=True))
        )
    )


def print_graph_by_nodes(graph: nx.MultiGraph):
    for u in graph.nodes:
        print(f"node {u} is connected to:")
        for v in graph.neighbors(u):
            for _, edge in graph.get_edge_data(u, v).items():
                print("  node: {:4d} by edge: {}".format(v, label_len(edge)))


def add_elevation_to_row_geometry(row, crs):
    geometry = row.geometry
    if geometry is not None:
        return add_elevation(geometry, crs)


def add_elevation(path: shapely.LineString, crs: int = 4326):
    transformer = pyproj.Transformer.from_crs(crs, 4326, always_xy=True)
    xy = path.coords.xy
    longitude, latitude = transformer.transform(*path.coords.xy)
    tmp = srtm.array_sample(latitude, longitude)
    return shapely.LineString([[x, y, z] for x, y, z in zip(*path.coords.xy, tmp)])
