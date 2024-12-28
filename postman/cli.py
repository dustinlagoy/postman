import argparse
import bisect
import dataclasses
import time

import geopandas
import matplotlib.pyplot as plt
import shapely

from postman import core, plot, preprocess, save, utils


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trail_file")
    parser.add_argument("-p", "--plot", action="store_true")
    parser.add_argument("-s", "--save")
    parser.add_argument("--save-segmented", action="store_true")
    args = parser.parse_args()
    trails = geopandas.read_file(args.trail_file)
    preprocess.add_elevation_stats(trails)
    clean_trails = preprocess.fix_trails(trails)
    utils.print_trails(clean_trails)
    graph = preprocess.to_graph(clean_trails)
    tour = core.trail_tour(graph, 6)
    utils.print_tour(tour)
    if args.save is not None:
        tracks = plot.tour_to_tracks(tour)
        for i, track in tracks.items():
            print("add z to", i, track.name)
            track.path = utils.add_elevation(track.path)
        with open(args.save, "w") as fp:
            fp.write(save.to_gpx(tracks, as_segments=args.save_segmented))
    if args.plot:
        # plot.plot_tracks(plot.tour_to_tracks(tour, 10.0))
        plot.plot_graph(graph)
        plot.plot_graph_with_trails(clean_trails, graph)
        plt.show()


if __name__ == "__main__" or __name__.startswith("bokeh_app"):
    main()
