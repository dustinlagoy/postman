import networkx as nx
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


def print_tour(tour: datatypes.Tour):
    length = 0
    total_up = 0
    total_down = 0
    for i, (_, _, data) in enumerate(tour):
        up = data["deniv_pos"]
        down = data["deniv_neg"]
        print("{:02d} {:8.2f} {:8.2f} {}".format(i, up, down, label_len(data)))
        length += data["distance"]
        total_up += up
        total_down += down
    print(
        "total length {:10.2f} up {:8.2f} down {:8.2f}".format(
            length, total_up, total_down
        )
    )


def print_trails(trails):
    for i in trails.iterrows():
        print(
            "{:02d} {:12.4f} {}".format(
                i[0], i[1]["distance"], str(i[1]["name"]).strip()
            )
        )
    print("total", sum(x.distance for _, x in trails.iterrows()))


def print_graph(graph):
    for i, (_, _, data) in enumerate(graph.edges(data=True)):
        print(
            "{:02d} {:12.4f} {}".format(i, data["distance"], str(data["name"]).strip())
        )
    print("total", sum(x["distance"] for _, _, x in graph.edges(data=True)))


def print_graph(graph: nx.MultiGraph):
    for u in graph.nodes:
        print(u)
        for v in graph.neighbors(u):
            print("  ", v)
            for _, edge in graph.get_edge_data(u, v).items():
                print("    ", label_len(edge))


def print_edges(graph):
    for i, item in enumerate(graph.edges.data()):
        print(
            "{:03d} {:03d} {:03d} {} {}".format(
                i, item[0], item[1], label(item[2]), item[2]["geometry"].length
            )
        )


def print_nodes(graph):
    for item in graph.nodes:
        edges = [graph.get_edge_data(*x)[0] for x in nx.edges(graph, item)]
        labels = [label(x) for x in edges]
        print(item, labels)


def add_elevation(path: shapely.LineString):
    return shapely.LineString([[x, y, srtm.sample(y, x)] for x, y in path.coords])
