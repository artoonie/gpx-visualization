#!/usr/bin/python

import datetime
import struct
import subprocess

def getTime(movieFilename):
    ATOM_HEADER_SIZE = 8
    # difference between Unix epoch and QuickTime epoch, in seconds
    EPOCH_ADJUSTER = 2082844800

    # open file and search for moov item
    f = open(movieFilename, "rb")
    while 1:
        atom_header = f.read(ATOM_HEADER_SIZE)
        print atom_header
        if atom_header[4:8] == 'moov':
            break
        else:
            atom_size = struct.unpack(">I", atom_header[0:4])[0]
            f.seek(atom_size - 8, 1)

    # Iterate through every character, since data is mixed and we
    # don't know how long each field is.
    # Null chars signify a new string.
    wordBuffer = ""
    words = []
    for i in range(0, 320):
        char = f.read(1)
        if char == '\0':
            if wordBuffer != "":
                words.append(wordBuffer)
                print i, wordBuffer
                wordBuffer = ""
        else:
            wordBuffer = wordBuffer + char

    # Magic: The 299th index contains the date.
    dateTimeIndex = 47
    dateTime = words[dateTimeIndex]
    year = int(dateTime[0:4])
    month = int(dateTime[5:7])
    day = int(dateTime[8:10])
    hour = int(dateTime[11:13])
    minute = int(dateTime[14:16])
    second = int(dateTime[17:19])
    return datetime.datetime(year, month, day, hour, minute, second)

def parseDatetime(datetimeString):
    # Return datetime from format '2016-07-02 20:24:59'
    year = int(datetimeString[0:4])
    month = int(datetimeString[5:7])
    day = int(datetimeString[8:10])
    hour = int(datetimeString[11:13])
    minute = int(datetimeString[14:16])
    second = int(datetimeString[17:19])
    return datetime.datetime(year, month, day, hour, minute, second)

def parseDuration(durationString):
    # Return datetime from format '00:00:04.80'
    hours = int(durationString[0:2])
    minutes = int(durationString[3:5])
    seconds = float(durationString[6:10])
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

def getCreationTimeAndDuration(filename):
    # Thanks http://stackoverflow.com/questions/3844430
    result = subprocess.Popen(["ffprobe", filename],
    stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    metadata = [x for x in result.stdout.readlines() if "Duration" in x or "creation_time" in x]
    creation = duration = None
    for m in metadata:
        if 'creation_time' in m:
            # Parse format: '      creation_time   : 2016-07-02 20:24:59'
            creation = parseDatetime(' '.join(m.split(' ')[-2:]))
        elif "Duration" in m:
            # Parse format: '  Duration: 00:00:04.80, start: 0.000000, bitrate: 17803 kb/s'
            duration = parseDuration(m.split(' ')[3])

    assert creation
    assert duration

    return creation, duration
