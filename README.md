# GPX Tracks To Movie

This is a small project to correspond my GPS location while on a bike ride with the video clips I shot during that ride.

It uses OpenStreetMaps to combine a visualization of GPX tracks with video clips.
The input is a GPX file (from Strava, for example) and a directory of videos taken while on that GPX route.
The output is a visualization of your GPS location for each video clip. Each visualization shows five minutes of travel starting at the beginning of the clip.

This is an in-progress prototype so there is no clean interface yet. Just dig in.

## Example: GPX visualizations
Combining all of the output visualizations into a single video. Each jump in the tracks is the start of another clip I took while on the bike ride.
![Aggregating the GPX visualizations into a single video](examles/gpx.gif)

## Example: Compositing GPX and clips
A simple example of what you could do with the output. Here, I overlayed three clips with their corresponding GPX tracks.
![Overlaying the visualization](examles/overlay.gif)
