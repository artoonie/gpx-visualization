import gpxpy 
import gpxpy.gpx
import matplotlib.pyplot as plt
import tilestitcher

def gpxVisitor(gpx):
    """ Visit each point in the strava GPX file. """
    for track in gpx.tracks: 
        for segment in track.segments: 
            for point in segment.points: 
                yield point

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

def visualizeGpxOnMap(slipy_map, gpx, mapImage, image_info):
    """ Draw a gpx track on the given mapImage.  """
    pts = [getImagePt(slipy_map, image_info, pt.latitude, pt.longitude)
            for pt in gpxVisitor(gpx)]

    # Create figure
    fig = plt.figure(facecolor = '0.05')

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
    plt.show()
    # plt.savefig('plot.png', dpi = 80)

def visualizeGpx(gpx):
    slipy_map = tilestitcher.SlippyMapTiles(max_tiles=10)
    (mapImage, imageInfo) = getMapImageAndImageInfoForGpx(slipy_map, gpx)
    visualizeGpxOnMap(slipy_map, gpx, mapImage, imageInfo)

if __name__ is "main":
    gpx_file = open('test.gpx', 'r') 
    gpx = gpxpy.parse(gpx_file) 
    visualizeGpx(gpx)
