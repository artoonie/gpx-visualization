# Parsing an existing file: 
# ------------------------- 

import tilestitcher
import gpxpy 
import gpxpy.gpx 

def gpxVisitor(gpx):
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

gpx_file = open('test.gpx', 'r') 
gpx = gpxpy.parse(gpx_file) 

for point in gpxVisitor(gpx):
    print 'SS Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)

border = 0.2
minLat = min(latitudeVisitor(gpx)) - border
maxLat = max(latitudeVisitor(gpx)) + border
minLon = min(longitudeVisitor(gpx)) - border
maxLon = max(longitudeVisitor(gpx)) + border

slipy_map = tilestitcher.SlippyMapTiles()
print minLat, maxLat, minLon, maxLon
image = slipy_map.get_image((minLat, maxLat), (minLon, maxLon), 200, 200)
image.show()
