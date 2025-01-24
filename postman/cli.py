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
    parser.add_argument("start_node", type=int)
    parser.add_argument("--print-graph", action="store_true")
    parser.add_argument("-p", "--plot", action="store_true")
    parser.add_argument("-s", "--save")
    parser.add_argument("--save-segmented", action="store_true")
    args = parser.parse_args()
    trails = geopandas.read_file(args.trail_file)
    for ax in trails.crs.axis_info:
        if ax.unit_code != "9001":
            raise RuntimeError("Data must be in meter-based projection")
    trails["geometry"] = trails.apply(
        utils.add_elevation_to_row_geometry, 1, args=(trails.crs,)
    )
    preprocess.add_elevation_stats(trails)
    clean_trails = preprocess.fix_trails(trails)
    print("preprocessed trails:")
    utils.print_trails(clean_trails)
    graph = preprocess.to_graph(clean_trails)
    if args.print_graph:
        print("graph edges:")
        utils.print_graph_by_edges(graph)
        print("graph nodes:")
        utils.print_graph_by_nodes(graph)
        return
    tour = core.trail_tour(graph, args.start_node)
    print("calculated tour:")
    utils.print_tour(tour)
    if args.save is not None:
        tracks = plot.tour_to_tracks(tour)
        tracks = utils.rearrange(tracks, [])
        for _, track in tracks.items():
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
