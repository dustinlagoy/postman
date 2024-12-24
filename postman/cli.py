import argparse
import bisect
import dataclasses
import time

import geopandas
import matplotlib.pyplot as plt
import shapely

from postman import core, plot, preprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trail_file")
    args = parser.parse_args()
    trails = geopandas.read_file(args.trail_file)
    print(type(trails))
    clean_trails = preprocess.fix_trails(trails)
    graph = preprocess.to_graph(clean_trails)
    path = core.trail_tour(graph, 6)
    plot.plot_graph(graph)
    plot.plot_graph_with_trails(clean_trails, graph)
    plot.plot_tour(path)
    plt.show()


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


if __name__ == "__main__":
    main()
