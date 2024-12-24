import networkx as nx


def label(x: dict):
    id = x.get("index_position", None)
    if id is None:
        print(type(x))
        id = x.name
    return "{:03d} {}".format(id, str(x["name"]).strip())


def label_len(x):
    return "{} {:.2f}".format(label(x), x["geometry"].length)


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
