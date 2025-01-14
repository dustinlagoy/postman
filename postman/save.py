import gpxpy

from postman import datatypes, utils


def to_gpx(
    tracks: datatypes.TrackCollection, name: str = "", as_segments=False, as_one=False
) -> str:
    gpx = gpxpy.gpx.GPX()
    gpx.name = name
    if as_segments or as_one:
        out_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(out_track)
    if as_one:
        segment = gpxpy.gpx.GPXTrackSegment()
        out_track.segments.append(segment)
    for id, track in tracks.items():
        if not as_segments and not as_one:
            out_track = gpxpy.gpx.GPXTrack(name=track.name, number=track.id)
            gpx.tracks.append(out_track)
        if not as_one:
            segment = gpxpy.gpx.GPXTrackSegment()
            out_track.segments.append(segment)
        for coord in track.path.coords:
            if len(coord) == 3:
                segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(coord[1], coord[0], coord[2])
                )
            else:
                segment.points.append(gpxpy.gpx.GPXTrackPoint(coord[1], coord[0]))
    return gpx.to_xml()
