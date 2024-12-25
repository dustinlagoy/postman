import argparse
import bisect
import dataclasses
import time

import geopandas
import matplotlib.pyplot as plt
import shapely

from postman import core, plot, preprocess, utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trail_file")
    args = parser.parse_args()
    trails = geopandas.read_file(args.trail_file)
    clean_trails = preprocess.fix_trails(trails)
    graph = preprocess.to_graph(clean_trails)
    tour = core.trail_tour(graph, 6)
    utils.print_tour(tour)
    plot.plot_tracks(plot.tour_to_tracks(tour))
    # plot.plot_graph(graph)
    # plot.plot_graph_with_trails(clean_trails, graph)
    # plot.plot_tour(path)
    # plt.show()


if __name__ == "__main__" or __name__.startswith("bokeh_app"):
    main()
