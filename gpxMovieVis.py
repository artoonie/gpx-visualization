import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import movietime
import os
import tilestitcher

# Helper class to cache some data so we don't have to redownload
# every frame
class GpxData():
    def __init__(self, gpx):
        slipyMap = tilestitcher.SlippyMapTiles(max_tiles=10)
        (mapImage, imageInfo) = getMapImageAndImageInfoForGpx(slipyMap, gpx)
        self.__init__(gpx, slipyMap, mapImage, imageInfo)

    def __init__(self, gpx, slipyMap, mapImage, imageInfo):
        self.gpx = gpx
        self.slipyMap = slipyMap
        self.mapImage = mapImage
        self.imageInfo = imageInfo

# Stupid 720p/1080p toggle
if True:
    # 720p
    movieWidth = 1280
    movieHeight = 720
else:
    # 1080p
    movieWidth = 1920
    movieHeight = 1080

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

def getMapImageAndImageInfoForGpx(slipyMap, gpx):
    minLat, maxLat, minLon, maxLon = gpx.get_bounds()
    return slipyMap.get_image((minLat, maxLat), (minLon, maxLon), movieWidth, movieHeight)

def getImagePt(slipyMap, imageInfo, lat, lon):
    return slipyMap._get_position_on_stitched_image(
        imageInfo.tile_1, imageInfo.tile_2, lat, lon)

def visualizeGpxOnMap(fig, slipyMap, gpx, mapImage, imageInfo):
    """ Draw a gpx track on the given mapImage.  """
    pts = [getImagePt(slipyMap, imageInfo, pt.latitude, pt.longitude)
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
    plt.plot(xPts, yPts, color = 'deepskyblue', lw = 10.0, alpha = 0.8)

    # Draw OSM image
    plt.imshow(mapImage, origin='upper', aspect='normal')

    return ax,

def visualizeGpx(gpx):
    slipyMap = tilestitcher.SlippyMapTiles(max_tiles=10)
    (mapImage, imageInfo) = getMapImageAndImageInfoForGpx(slipyMap, gpx)
    visualizeGpxOnMap(slipyMap, gpx, mapImage, imageInfo)

def getPointsFrom(gpxSegment, startFrame, numFrames):
    count = 0
    startPoint = gpx.tracks[0].segments[0].points[startFrame]
    for pt in gpxSegment.walk(startPoint):
        if count == numFrames: return
        yield pt
        count = count+1

    # If this is hit, numFrames exceeds total number of frames
    assert False

def getPointsBetween(gpxSegment, startPoint, endPoint):
    for pt in gpxSegment.walk(startPoint):
        yield pt
        if pt == endPoint: return

    # If this is hit, endPoint is not a point after startPoint
    raise Exception("endPoint not a part of this segment")

def visualizeGpxAtTime(frame, fig, gpxData, startPoint, endPoint, numFrames):
    print "Frame ", frame, "/", numFrames
    numPoints = gpxData.gpx.get_points_no()

    segment = getSegment(gpxData.gpx)
    subGpx = [x for x in getPointsBetween(gpxData.gpx, startPoint, endPoint)]
    return visualizeGpxOnMap(fig, gpxData.slipyMap, subGpx, gpxData.mapImage, gpxData.imageInfo)

def makeMovieForDuration(gpxData, creationTime, duration, outputFilename):
    sizeX = movieWidth / 40
    sizeY = movieHeight / 40
    fig = plt.figure(figsize=(sizeX, sizeY), dpi=1) # @ dpi 40 = 1080p

    startFrame = gpxData.gpx.get_location_at(creationTime)[0]
    endFrame = gpxData.gpx.get_location_at(creationTime+duration)[0]
    numFrames = 1 + duration.seconds/500
    if startFrame == endFrame:
        raise Exception("GPX and MOV times don't overlap")

    lineAni = animation.FuncAnimation(fig, visualizeGpxAtTime, frames=numFrames,
        fargs=(fig, gpxData, startFrame, endFrame, numFrames),
        interval=25, blit=False)
    lineAni.save(outputFilename, fps=5)


def makeVisForEachMovie(gpxData, inputDir, outputDir):
    for i in os.listdir(inputDir):
        if i.endswith(".MOV"):
            inputFn = os.path.join(inputDir, i)
            outputFn = os.path.join(outputDir, os.path.splitext(i)[0]+'.mp4')
            if os.path.exists(outputFn):
                print "Skipping", inputFn
                continue
            ctAndD = movietime.getCreationTimeAndDuration(inputFn)

            try:
                makeMovieForDuration(gpxData, ctAndD[0], ctAndD[1], outputFn)
                print "Generated", outputFn
            except:
                print "Failed for video", inputFn

if __name__ == "__main__":
    gpxFile = open('test.gpx', 'r')
    gpx = gpxpy.parse(gpxFile)
    animateGpx(gpx, 'test.mp4')
    gpxData = GpxData(gpx)
    test.makeVisForEachMovie(gpxData, 'vidDir', 'visDir')
