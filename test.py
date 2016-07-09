import gpxpy 
import gpxpy.gpx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tilestitcher

def gpxVisitor(gpx):
    """ Visit each point in the strava GPX file. """
    if hasattr(gpx, 'tracks'):
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    yield point
    else:
        for point in gpx:
            yield point

def getSegment(gpx):
    """ Assume there is only one segment, and return it. """
    assert len(gpx.tracks) == 1
    track = gpx.tracks[0]
    assert len(track.segments) == 1
    return track.segments[0]

def latitudeVisitor(gpx):
    for point in gpxVisitor(gpx):
        yield point.latitude

def longitudeVisitor(gpx):
    for point in gpxVisitor(gpx):
        yield point.longitude

def getMapImageAndImageInfoForGpx(slipy_map, gpx):
    minLat, maxLat, minLon, maxLon = gpx.get_bounds()
    return slipy_map.get_image((minLat, maxLat), (minLon, maxLon), 1920, 1080)

def getImagePt(slipy_map, image_info, lat, lon):
    return slipy_map._get_position_on_stitched_image(
        image_info.tile_1, image_info.tile_2, lat, lon)

def visualizeGpxOnMap(fig, slipy_map, gpx, mapImage, image_info):
    """ Draw a gpx track on the given mapImage.  """
    pts = [getImagePt(slipy_map, image_info, pt.latitude, pt.longitude)
            for pt in gpxVisitor(gpx)]

    fig.clear()

    # Remove axes
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    fig.set_tight_layout(True)

    # Draw gpx points
    # TODO! HACK! Why does this require a shift??
    xPts = [p[0]-120  for p in pts]
    yPts = [p[1]-177 for p in pts]
    plt.plot(xPts, yPts, color = 'deepskyblue', lw = 2.0, alpha = 0.8)

    # Draw OSM image
    plt.imshow(mapImage, origin='upper', aspect='normal')

    # Visualization
    #plt.show()
    #plt.savefig('plot.png', dpi = 80)

    return ax,

def visualizeGpx(gpx):
    slipy_map = tilestitcher.SlippyMapTiles(max_tiles=10)
    (mapImage, imageInfo) = getMapImageAndImageInfoForGpx(slipy_map, gpx)
    visualizeGpxOnMap(slipy_map, gpx, mapImage, imageInfo)

def getPointsFrom(gpxSegment, startPoint, numFrames):
    count = 0
    for pt in gpxSegment.walk(startPoint):
        if count == numFrames: return
        yield pt
        count = count+1

    # If this is hit, numFrames exceeds total number of frames
    assert False

def getPointsBetween(gpxSegment, startPoint, endPoint):
    for pt in gpxSegment.walk(startPoint):
        if pt == endPoint: return
        yield pt

    # If this is hit, endPoint is not a point after startPoint
    assert False

def visualizeGpxAtTime(numFrames, fig, gpx, timeStart, slipy_map, mapImage, image_info):
    print numFrames
    segment = getSegment(gpx)
    startPoint = segment.get_location_at(timeStart)
    subGpx = [x for x in getPointsFrom(segment, startPoint, 1000+numFrames*100)]
    return visualizeGpxOnMap(fig, slipy_map, subGpx, mapImage, image_info)

def animateGpxAtTime(gpx, timeStart, timeEnd, slipy_map, mapImage, image_info):
    fig = plt.figure(facecolor = '0.05')
    line_ani = animation.FuncAnimation(fig, visualizeGpxAtTime, frames=100,
        fargs=(fig, gpx, timeStart, slipy_map, mapImage, image_info),
        interval=50, blit=False)

if __name__ is "main":
    gpx_file = open('test.gpx', 'r') 
    gpx = gpxpy.parse(gpx_file) 
    visualizeGpx(gpx)
