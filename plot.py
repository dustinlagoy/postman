import geoviews as gv
import holoviews as hv
import numpy as np
from bokeh.models import ColumnDataSource, CustomJSHover, HoverTool
from cartopy import crs

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
    print("nodes", nodes)
    plot *= plot_nodes(nodes)
    print(plot)
    renderer.server_doc(plot)


def plot_many_tracks(tracks: datatypes.TrackCollection):
    show_legend = False
    data = {}
    output = []
    for id, track in list(tracks.items()):
        # should be able to add color to each item as dictionary value
        # output.append(track.path.coords)
        output.append(
            {
                "Longitude": track.path.coords.xy[0],
                "Latitude": track.path.coords.xy[1],
                "name": track.name,
                "id": id,
            }
        )

        # points = [(x[0], x[1]) for x in track.path.simplify(0.001).coords]
        # print(track.name, len(track.path.coords), len(points))
        # path = gv.Path(points, label=f"{id} {track.name}").opts(
        #     line_width=3, show_legend=show_legend
        # )
        # hover = HoverTool(
        #     tooltips=[
        #         ("name", f"{id} {track.name}"),
        #         ("lon", "$x{custom}"),
        #         ("lat", "$y{custom}"),
        #         ("edges", f"{track.start} to {track.end}"),
        #     ],
        #     formatters={
        #         "$x": CustomJSHover(code=lat_lon_js.format(0)),
        #         "$y": CustomJSHover(code=lat_lon_js.format(1)),
        #     },
        #     point_policy="follow_mouse",
        # )
        # output.append(path.opts(tools=[hover]))
        # output.append(path.opts())

    # return [gv.Path(output).opts(line_width=3, show_legend=True)]
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
    print(len(output))
    # use contours due to https://github.com/holoviz/holoviews/issues/4862
    return [
        gv.Contours(output, vdims=["name", "id"]).opts(
            cmap="hsv",
            color="id",
            line_width=3,
            tools=[hover],
        )
    ]


def plot_nodes(nodes: datatypes.NodeCollection):
    # text = [f"{i} tracks: {repr(x.name)}" for i, x in nodes.items()]
    hover = HoverTool(
        tooltips=[
            ("lon", "$x{custom}"),
            ("lat", "$y{custom}"),
            ("node", "@name"),
            # ("node", "$index{custom}"),
        ],
        formatters={
            "$x": CustomJSHover(code=lat_lon_js.format(0)),
            "$y": CustomJSHover(code=lat_lon_js.format(1)),
            # "$index": CustomJSHover(
            #     args=dict(nodes=ColumnDataSource(dict(text=text))), code=node_js
            # ),
        },
        point_policy="follow_mouse",
    )
    return gv.Points(
        [
            {"Longitude": x.point.x, "Latitude": x.point.y, "name": x.name}
            for x in nodes.values()
        ],
        vdims=["name"],
    ).opts(size=10, tools=[hover], color="red")
