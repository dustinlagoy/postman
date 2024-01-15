import geoviews as gv
import holoviews as hv

import datatypes


def plot_tracks(tracks: datatypes.TrackCollection, nodes: datatypes.NodeCollection):
    renderer = hv.renderer("bokeh")
    plot = gv.tile_sources.OpenTopoMap
    plot = plot.opts(height=800, width=1600)
    show_legend = True
    for track in tracks.values():
        points = [(x[0], x[1]) for x in track.path.coords]
        plot *= gv.Path(points, label=track.name).opts(
            line_width=3, show_legend=show_legend
        )
        # plot *= gv.Points(points, label=track.name).opts(
        #     show_legend=show_legend, size=10, alpha=0.5
        # )
    plot *= gv.Labels(
        {
            ("Longitude", "Latitude"): [
                (
                    x.path.coords[int(len(x.path.coords) / 2)][0],
                    x.path.coords[int(len(x.path.coords) / 2)][1],
                )
                for x in tracks.values()
            ],
            "text": [x.name for x in tracks.values()],
        },
        ["Longitude", "Latitude"],
        "text",
    )
    plot *= gv.Points([(x.point.x, x.point.y) for x in nodes.values()]).opts(size=10)
    renderer.server_doc(plot)
