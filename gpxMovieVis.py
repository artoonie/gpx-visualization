import datetime
import os

import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tilestitcher

import movietime

# Helper class to cache some data so we don't have to redownload
# every frame
class GpxData():
    def __init__(self, gpx, slipyMap=None, mapImage=None, imageInfo=None):
        self.gpx = gpx
        if slipyMap:
            assert mapImage
            assert imageInfo
            self.slipyMap = slipyMap
            self.mapImage = mapImage
            self.imageInfo = imageInfo
        else:
            self.slipyMap = tilestitcher.SlippyMapTiles(max_tiles=10)
            (self.mapImage, self.imageInfo) = getMapImageAndImageInfoForGpx(\
                self.slipyMap, self.gpx)

# Stupid 720p/1080p toggle
use720 = True
if use720:
    # 720p
    movieWidth = 1280
    movieHeight = 720
    lineWeight = 2
else:
    # 1080p
    movieWidth = 1920
    movieHeight = 1080
    lineWeight = 10

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

def getMapImageAndImageInfoForGpx(slipyMap, gpx):
    minLat, maxLat, minLon, maxLon = gpx.get_bounds()
    return slipyMap.get_image((minLat, maxLat), (minLon, maxLon), movieWidth, movieHeight, attribution = "")

def getImagePt(slipyMap, imageInfo, lat, lon):
    return slipyMap.get_position_on_cropped_image(imageInfo, lat, lon)

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
    xPts = [p[0] for p in pts]
    yPts = [p[1] for p in pts]
    plt.plot(xPts, yPts, color = 'deepskyblue', lw = lineWeight, alpha = 0.8)

    # Draw OSM image
    plt.imshow(mapImage, origin='upper', aspect='normal')

    return ax,

def visualizeGpx(gpx):
    slipyMap = tilestitcher.SlippyMapTiles(max_tiles=10)
    (mapImage, imageInfo) = getMapImageAndImageInfoForGpx(slipyMap, gpx)
    fig = plt.figure()
    visualizeGpxOnMap(fig, slipyMap, gpx, mapImage, imageInfo)
    plt.show()

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

def visualizeGpxAtTime(frame, fig, gpxData, startPoint, duration, numFrames):
    print "Frame ", frame+1, "/", numFrames

    alpha = float(frame+1)/numFrames
    lerpdDuration = datetime.timedelta(seconds = duration.seconds * alpha)
    endTime = startPoint.time + lerpdDuration
    endPoint = gpxData.gpx.get_location_at(endTime)[0]
    
    subGpx = [x for x in getPointsBetween(gpxData.gpx, startPoint, endPoint)]
    return visualizeGpxOnMap(fig, gpxData.slipyMap, subGpx, gpxData.mapImage, gpxData.imageInfo)

def makeMovieForDuration(gpxData, creationTime, duration, outputFilename):
    sizeX = movieWidth / 100
    sizeY = movieHeight / 100
    fig = plt.figure(figsize=(sizeX, sizeY)) # @ dpi 40

    minDuration = datetime.timedelta(minutes=5)
    if duration.seconds < minDuration.seconds: duration = minDuration

    startPoint = gpxData.gpx.get_location_at(creationTime)[0]
    endTime = creationTime+duration
    endPointList = gpxData.gpx.get_location_at(endTime)
    if not endPointList:
        raise Exception("End time {} not in this GPX data".format(endTime))
    else:
        endPoint = endPointList[0]

    numFrames = 1 + duration.seconds/10
    if startPoint == endPoint:
        raise Exception("GPX and MOV times don't overlap")

    lineAni = animation.FuncAnimation(fig, visualizeGpxAtTime, frames=numFrames,
        fargs=(fig, gpxData, startPoint, duration, numFrames),
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
            except Exception as e:
                print "Failed for video", inputFn, "because of error:", e.message
            finally:
                plt.clf()

def getTestGpxData():
    gpxFile1 = open('pt1.gpx', 'r')
    gpx = gpxpy.parse(gpxFile1)
    gpxFile2 = open('pt2.gpx', 'r')
    gpx2 = gpxpy.parse(gpxFile2)
    gpx.tracks.extend(gpx2.tracks)
    gpxData = GpxData(gpx)
    return gpxData

if __name__ == "__main__":
    gpxFile = open('test.gpx', 'r')
    gpx = gpxpy.parse(gpxFile)
    gpxData = GpxData(gpx)

    animateGpx(gpx, 'test.mp4')
    makeVisForEachMovie(gpxData, 'vidDir', 'visDir')
    visualizeGpx(gpxData)
