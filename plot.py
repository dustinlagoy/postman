import geoviews as gv
import holoviews as hv
from bokeh.models import ColumnDataSource, CustomJSHover, HoverTool

import datatypes

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


def plot_tracks(tracks: datatypes.TrackCollection, nodes: datatypes.NodeCollection):
    renderer = hv.renderer("bokeh")
    tools = ["pan", "wheel_zoom", "box_zoom", "undo", "redo", "reset"]
    plot = gv.tile_sources.OpenTopoMap.opts(tools=tools, height=800, width=800)
    for item in plot_many_tracks(tracks):
        plot *= item
    plot *= plot_nodes(nodes)
    renderer.server_doc(plot)


def plot_many_tracks(tracks: datatypes.TrackCollection):
    show_legend = False
    data = {}
    output = []
    for id, track in tracks.items():
        points = [(x[0], x[1]) for x in track.path.coords]
        path = gv.Path(points, label=f"{id} {track.name}").opts(
            line_width=3, show_legend=show_legend
        )
        hover = HoverTool(
            tooltips=[
                ("name", f"{id} {track.name}"),
                ("lon", "$x{custom}"),
                ("lat", "$y{custom}"),
                ("edges", f"{track.start} to {track.end}"),
            ],
            formatters={
                "$x": CustomJSHover(code=lat_lon_js.format(0)),
                "$y": CustomJSHover(code=lat_lon_js.format(1)),
            },
            point_policy="follow_mouse",
        )
        output.append(path.opts(tools=[hover]))
        
    return output


def plot_nodes(nodes: datatypes.NodeCollection):
    text = [f"{i} tracks: {repr(x.tracks)}" for i, x in nodes.items()]
    hover = HoverTool(
        tooltips=[
            ("lon", "$x{custom}"),
            ("lat", "$y{custom}"),
            ("node", "$index{custom}"),
        ],
        formatters={
            "$x": CustomJSHover(code=lat_lon_js.format(0)),
            "$y": CustomJSHover(code=lat_lon_js.format(1)),
            "$index": CustomJSHover(
                args=dict(nodes=ColumnDataSource(dict(text=text))), code=node_js
            ),
        },
        point_policy="follow_mouse",
    )
    return gv.Points([(x.point.x, x.point.y) for x in nodes.values()]).opts(
        size=10, tools=[hover]
    )
