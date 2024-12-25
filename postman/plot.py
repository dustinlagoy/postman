import array

import geoviews as gv
import holoviews as hv
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pyproj
import shapely.plotting
from bokeh.models import ColumnDataSource, CustomJSHover, HoverTool
from cartopy import crs

from postman import datatypes, utils

lat_lon_js = """
    const projections = Bokeh.require("core/util/projections");
    const x = special_vars.x
    const y = special_vars.y
    const coords = projections.wgs84_mercator.invert(x, y)
    return coords[{:d}].toFixed(9)
"""

node_js = """
    const id = special_vars.index
    return nodes.data.text[id]
"""


def geoframe_to_tracks(df) -> datatypes.TrackCollection:
    out: datatypes.TrackCollection = {}
    transformer = pyproj.Transformer.from_crs(32610, 4326)
    for id, track in df.iterrows():
        latitude, longitude = transformer.transform(*track["geometry"].coords.xy)
        if latitude[-1] == latitude[-2]:
            latitude = latitude[:-1]
            longitude = longitude[:-1]
        out[id] = datatypes.Track(
            utils.label_len(track),
            shapely.LineString([[x, y] for x, y in zip(longitude, latitude)]),
        )
    return out


def tour_to_tracks(tour: datatypes.Tour) -> datatypes.TrackCollection:
    out: datatypes.TrackCollection = {}
    transformer = pyproj.Transformer.from_crs(32610, 4326)
    seen: list[int] = []
    for i, (_, _, data) in enumerate(tour):
        id = data["index_position"]
        offset_count = seen.count(id)
        x, y = data["geometry"].offset_curve(offset_count * 10).coords.xy
        seen.append(id)
        latitude, longitude = transformer.transform(x, y)
        if latitude[-1] == latitude[-2] or longitude[-1] == longitude[-2]:
            latitude = latitude[:-1]
            longitude = longitude[:-1]
        out[i] = datatypes.Track(
            utils.label_len(data),
            shapely.LineString([[x, y] for x, y in zip(longitude, latitude)]),
        )
    return out


def plot_tracks(tracks: datatypes.TrackCollection):
    renderer = hv.renderer("bokeh")
    tools = ["pan", "wheel_zoom", "box_zoom", "undo", "redo", "reset"]
    plot = gv.tile_sources.OpenTopoMap.opts(
        tools=tools, responsive=True
    )  # , height=800, width=800)
    plot *= _plot_tracks(tracks)
    # print("nodes", nodes)
    # plot *= plot_nodes(nodes)
    renderer.server_doc(plot)


def _plot_tracks(tracks: datatypes.TrackCollection):
    show_legend = False
    output = []
    for id, track in list(tracks.items()):
        # should be able to add color to each item as dictionary value
        # output.append(track.path.coords)
        print(id, type(id), track.name, type(track.name))
        output.append(
            {
                "Longitude": track.path.coords.xy[0],
                "Latitude": track.path.coords.xy[1],
                "name": track.name,
                "id": id,
            }
        )
    hover = HoverTool(
        tooltips=[
            ("name", "@name"),
            ("id", "@id"),
            ("lon", "$x{custom}"),
            ("lat", "$y{custom}"),
        ],
        formatters={
            "$x": CustomJSHover(code=lat_lon_js.format(0)),
            "$y": CustomJSHover(code=lat_lon_js.format(1)),
        },
        point_policy="follow_mouse",
    )
    return gv.Contours(output, vdims=["name", "id"]).opts(
        cmap="brg", color="id", line_width=3, tools=[hover]
    )


def plot_graph(graph):
    _, axis = plt.subplots(1, 1, figsize=(12, 6), sharex=True, sharey=True)
    _plot_graph(graph, axis, False)
    plt.tight_layout()


def plot_graph_with_trails(trails, graph):
    _, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
    plot_trails(trails, axes[0])
    _plot_graph(graph, axes[1], True)
    for i, facet in enumerate(axes):
        facet.set_title(("Map", "Graph")[i])
        facet.axis("off")
    plt.tight_layout()


def plot_tour(tour):
    _, axis = plt.subplots(1, 1, figsize=(12, 6))
    plot_path(tour, axis)
    plt.tight_layout()


def plot_path(path, axis):
    length = 0
    seen = []
    # cmap = matplotlib.cm.get_cmap("brg")
    cmap = matplotlib.cm.get_cmap("viridis")
    for i, (u, v, data) in enumerate(path):
        print(i, utils.label_len(data))
        length += data["distance"]
        offset_count = seen.count(data)
        seen.append(data)
        color = cmap(i / len(path))
        curve = data["geometry"].offset_curve(offset_count * 5)
        center = curve.line_interpolate_point(0.5, normalized=True)
        shapely.plotting.plot_line(curve, axis, add_points=False, color=color)
        axis.text(center.x, center.y, i, color="r", size="large")
    print(length)


def _plot_graph(graph, axis, geometric=False):
    if geometric:
        positions = {n[0]: [n[1]["x"], n[1]["y"]] for n in list(graph.nodes.data())}
    else:
        positions = nx.spring_layout(graph)
    names = {(x[0], x[1]): utils.label_len(x[2]) for x in graph.edges.data()}
    nx.draw(graph, positions, ax=axis, node_size=10)
    nx.draw_networkx_labels(
        graph, positions, ax=axis, font_color="r", font_weight="bold"
    )
    nx.draw_networkx_edge_labels(graph, positions, names, ax=axis, node_size=10)


def plot_trails(trails, axis):
    trails.plot(color="k", ax=axis)
    trails.apply(
        lambda x: axis.annotate(
            text=utils.label_len(x), xy=x.geometry.centroid.coords[0], ha="center"
        ),
        axis=1,
    )
