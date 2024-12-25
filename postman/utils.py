import networkx as nx

from postman import datatypes


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
    total = 0
    for i, (_, _, data) in enumerate(tour):
        print("{:02d} {}".format(i, label_len(data)))
        total += data["distance"]
    print("total", total)


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
