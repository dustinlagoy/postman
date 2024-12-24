import sys
from itertools import combinations

import geopandas
import matplotlib.pyplot as plt
import momepy
import networkx as nx
import numpy as np


def main():
    trails = geopandas.read_file(
        "/home/dustin/documents/maps/nickel-plate/umtt_trimmed_with_z_and_stats_two.shp"
    )
    for i in trails.iterrows():
        print(
            "{:02d} {:12.4f} {}".format(
                i[0], i[1]["distance"], str(i[1]["name"]).strip()
            )
        )
    print("total", sum(x.distance for _, x in trails.iterrows()))
    new = preprocess(trails)
    for i, item in new.iterrows():
        print(i, label_len(item), item.geometry.coords[0], item.geometry.coords[-1])
    print("total", sum(x.distance for _, x in new.iterrows()))
    graph = to_network(new)
    for i, (_, _, data) in enumerate(graph.edges(data=True)):
        print(
            "{:02d} {:12.4f} {}".format(i, data["distance"], str(data["name"]).strip())
        )
    print("total", sum(x["distance"] for _, _, x in graph.edges(data=True)))
    ax = plot_both(new, graph)
    plot_one(graph)
    path = trail_tour(graph, graph.get_edge_data(5, 6)[0], ax)
    plt.show()


def trail_tour(graph, start, ax):
    # euler = nx.eulerize(graph)
    euler = weighted_eulerize(graph, "distance")
    euler_start = None
    for u, v, data in euler.edges(data=True):
        if data["distance"] == start["distance"]:
            euler_start = u
    path = nx.eulerian_circuit(euler, euler_start, keys=True)
    length = 0
    seen = []
    for i, (u, v, k) in enumerate(path):
        data = euler.get_edge_data(u, v)[k]
        # print(i, u, v, k, euler.get_edge_data(u, v))
        print(i, label_len(data))  # , label(item))
        length += data["distance"]
        center = data["geometry"].line_interpolate_point(0.5, normalized=True)
        if center in seen:
            ax.text(center.x + 15, center.y + 15, i, color="r", size="large")
        else:
            seen.append(center)
            ax.text(center.x, center.y, i, color="r", size="large")
    print(length)
    return path

    # weighted = add_average_weight(graph)
    # supergraph = find_euler_supergraph(graph)
    # tour = find_tour(supergraph)


def multigraph_path_length(G, P, weight="weight"):
    length = 0
    for i in range(len(P) - 1):
        minimum = None
        for _, data in G.get_edge_data(P[i], P[i + 1]).items():
            if minimum is None:
                minimum = data[weight]
            else:
                minimum = min(minimum, data[weight])
        assert minimum is not None
        length += minimum
    return length


def multigraph_shortest_path(G, P, weight="weight"):
    out_path = []
    for i in range(len(P) - 1):
        m = P[i]
        n = P[i + 1]
        minimum = None
        for _, data in G.get_edge_data(m, n).items():
            if minimum is None:
                minimum = data
            elif data[weight] < minimum[weight]:
                minimum = data
        assert minimum is not None
        out_path.append((m, n, minimum))
    return out_path


def weighted_eulerize(G, weight="weight"):
    if G.order() == 0:
        raise nx.NetworkXPointlessConcept("Cannot Eulerize null graph")
    if not nx.is_connected(G):
        raise nx.NetworkXError("G is not connected")
    odd_degree_nodes = [n for n, d in G.degree() if d % 2 == 1]
    print("odd degree nodes", len(odd_degree_nodes))
    G = nx.MultiGraph(G)
    if len(odd_degree_nodes) == 0:
        return G

    # get all shortest paths between vertices of odd degree
    odd_deg_pairs_paths = [
        (m, {n: nx.shortest_path(G, source=m, target=n, weight=weight)})
        for m, n in combinations(odd_degree_nodes, 2)
    ]
    print(odd_deg_pairs_paths)
    print("odd degree pairs", len(odd_deg_pairs_paths))

    # use the number of vertices in a graph + 1 as an upper bound on
    # the maximum length of a path in G
    # upper_bound_on_max_path_length = len(G) + 1
    upper_bound_on_max_path_length = (
        sum(x[weight] for _, _, x in G.edges(data=True)) + 1
    )
    # TODO keep updating below

    # use "len(G) + 1 - len(P)",
    # where P is a shortest path between vertices n and m,
    # as edge-weights in a new graph
    # store the paths in the graph for easy indexing later
    Gp = nx.Graph()
    for n, Ps in odd_deg_pairs_paths:
        for m, P in Ps.items():
            if n != m:
                # note should just remove longer paths between nodes (as they
                # will never be part of a shortest path) before finding shorter
                # paths above as noted in
                # https://groups.google.com/g/networkx-discuss/c/87uC9F0ug8Y/m/CrNNYEHLZfIJ
                # instead assume that is what the shortest path algorithm did
                length = multigraph_path_length(G, P, weight)
                print(n, m, P, length)
                Gp.add_edge(
                    m, n, weight=upper_bound_on_max_path_length - length, path=P
                )

    # find the minimum weight matching of edges in the weighted graph
    best_matching = nx.Graph(list(nx.max_weight_matching(Gp)))

    # duplicate each edge along each path in the set of paths in Gp
    for m, n in best_matching.edges():
        path = multigraph_shortest_path(G, Gp[m][n]["path"], weight)
        print(m, n, end="")
        for u, v, p in path:
            print(" ", u, v, label_len(p), end="")
        print()
        # G.add_edges_from(nx.utils.pairwise(path))
        G.add_edges_from(path)
    return G


def add_average_weight(graph):
    pass


def find_euler_supergraph(graph):
    # need to have even number of edges connected to each node to be eulerian graph
    # can duplicate each edge (e) x_e times to achieve this
    # need to find x_e (for each edge)
    n_nodes = 0
    d_n_plus = np.zeros(n_nodes) + np.inf
    d_n_minus = np.zeros(n_nodes)
    y_n = np.zeros(n_nodes)
    for i, node in enumerate(graph.nodes):
        d_n_plus

    pass


def find_tour(graph):
    pass


def plot_graph(graph, axis, geometric=False):
    if geometric:
        positions = {n[0]: [n[1]["x"], n[1]["y"]] for n in list(graph.nodes.data())}
    else:
        positions = nx.spring_layout(graph)
    names = {(x[0], x[1]): label_len(x[2]) for x in graph.edges.data()}
    nx.draw(graph, positions, ax=axis, node_size=10)
    nx.draw_networkx_labels(
        graph, positions, ax=axis, font_color="r", font_weight="bold"
    )
    nx.draw_networkx_edge_labels(graph, positions, names, ax=axis, node_size=10)


def plot_one(graph):
    _, axis = plt.subplots(1, 1, figsize=(12, 6), sharex=True, sharey=True)
    plot_graph(graph, axis, False)
    plt.tight_layout()


def plot_both(trails, graph):
    _, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
    trails.plot(color="k", ax=axes[0])
    trails.apply(
        lambda x: axes[0].annotate(
            text=label_len(x), xy=x.geometry.centroid.coords[0], ha="center"
        ),
        axis=1,
    )
    for i, facet in enumerate(axes):
        facet.set_title(("Map", "Graph")[i])
        facet.axis("off")
    plot_graph(graph, axes[1], True)
    plt.tight_layout()
    return axes[0]


def label(x: dict):
    id = x.get("index_position", None)
    if id is None:
        id = x.name
    return "{:03d} {}".format(id, str(x["name"]).strip())


def label_len(x):
    return "{} {:.2f}".format(label(x), x["geometry"].length)


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


def preprocess(trails: geopandas.GeoDataFrame):
    # remove any empty geometries
    new = trails.drop(trails[trails.geometry == None].index)
    # fix bad connections, the order seems to matter here
    new = momepy.extend_lines(new, 1.0)
    new.geometry = momepy.close_gaps(new, 0.1)
    new = momepy.remove_false_nodes(new)
    new = fix_nans(trails, new)
    new.geometry = momepy.close_gaps(new, 0.1)
    # new = remove_empties(new)
    return new


def remove_empties(new):
    print(len(new))
    for i, item in new.iterrows():
        print(i, item["geometry"] is None, item["distance"])
    print(len(new["geometry"] != None))
    tmp = new[new["geometry"] != None]
    sys.exit()


def fix_nans(old, new):
    keys = [
        "name",
        "number",
        "distance",
        "max_elevat",
        "min_elevat",
        "deniv_pos",
        "deniv_neg",
        "kme",
    ]
    for i, row in new.iterrows():
        if np.isnan(row["distance"]):
            distance = row["geometry"].length
            # print(i, distance)
            for j, other in old.iterrows():
                if abs(other["distance"] - distance) < 0.1:
                    # print("    ", j, other["distance"])
                    for key in keys:
                        new.at[i, key] = other[key]
    return new


def to_network(trails):
    return momepy.gdf_to_nx(
        trails, approach="primal", integer_labels=True, preserve_index=True
    )


if __name__ == main():
    main()
