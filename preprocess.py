import sys

import geopandas
import matplotlib.pyplot as plt
import momepy
import networkx as nx


def label(x: dict):
    id = x.get("index_position", None)
    if id is None:
        id = x.name
    return "{:03d} {}".format(id, str(x["name"]).strip())


def label_len(x):
    return "{} {:.2f}".format(label(x), x["geometry"].length)


# paths = geopandas.read_file("/home/dustin/documents/maps/nickel-plate/umtt_split.shp")
paths = geopandas.read_file(
    "/home/dustin/documents/maps/nickel-plate/umtt_trimmed_with_z_and_stats.shp"
)
print(paths)
# for item in paths["geometry"]:
#     print(type(item))
for item in paths.iterrows():
    print(item[0], item[1]["number"], str(item[1]["name"]).strip())
# sys.exit()
print(paths.geometry)
print(paths["geometry"])
paths = paths.drop(paths[paths.geometry == None].index)
print(paths)
paths = momepy.extend_lines(paths, 1.0)
paths.geometry = momepy.close_gaps(paths, 0.1)
paths = momepy.remove_false_nodes(paths)
graph = momepy.gdf_to_nx(
    paths, approach="primal", integer_labels=True, preserve_index=True
)
print(graph)
# sys.exit()
sum = 0
for i, item in enumerate(graph.edges.data()):
    print(
        "{:03d} {:03d} {:03d} {} {}".format(
            i, item[0], item[1], label(item[2]), item[2]["geometry"].length
        )
    )
    sum += item[2]["geometry"].length
print("total", sum)
for item in graph.nodes:
    edges = [graph.get_edge_data(*x)[0] for x in nx.edges(graph, item)]
    labels = [label(x) for x in edges]
    print(item, labels)

# sys.exit()

# f, ax = plt.subplots(1, 1, figsize=(12, 6), sharex=True, sharey=True)
# ax = [ax]
f, ax = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
paths.plot(color="k", ax=ax[1])
paths.apply(
    lambda x: ax[1].annotate(
        text=label_len(x), xy=x.geometry.centroid.coords[0], ha="center"
    ),
    axis=1,
)
for i, facet in enumerate(ax):
    facet.set_title(("Graph", "Map")[i])
    facet.axis("off")

positions = {n[0]: [n[1]["x"], n[1]["y"]] for n in list(graph.nodes.data())}
names = {(x[0], x[1]): label_len(x[2]) for x in graph.edges.data()}
# positions = nx.spring_layout(graph)
nx.draw(graph, positions, ax=ax[0], node_size=10)
# nx.draw_networkx(graph, positions, ax=ax[1], node_size=10)
nx.draw_networkx_edge_labels(graph, positions, names, ax=ax[0], node_size=10)
# nx.draw(graph, ax=ax[1], node_size=10)
plt.tight_layout()
plt.show()
