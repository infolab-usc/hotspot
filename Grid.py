__author__ = 'ubriela'

from Params import Params

import SwaggerMediaq as sm
import geojson
from geojson import Feature, Point, FeatureCollection
import requests
import json
import sys
import math
import re
import numpy as np
import time
import matplotlib.pyplot as plt
import itertools
import csv

from FOV import FOV
from Video import Video
from Params import Params
from UtilsBDR import mbr_to_cellids, cell_coord, distance_km

#url = "http://mediaq.usc.edu/MediaQ_MVC_V3/api"
url = "http://mediaq1.cloudapp.net/MediaQ_MVC_V3/api"
validate_endpoint = 'http://geojsonlint.com/validate'

VIDEO_FILE = "dataset/FOVMetadata.txt"
IS_FROM_MEDIAQ = False # true --> obtain from mediaq; otherwise, retrieve from file
VALIDATE_GEOJSON = False
"""
videoid 0
fovid 1
lat 2
lon 3
dir 4
r 7
theta 8
timestamp 9
"""

"""
1.5GB --> 1500
1.5MB --> 1.5
250K --> 0.25
"""
def size_in_mb(size):
    if size:
        value = re.sub("[^0-9.]", "", size)
        unit = re.sub("[^a-zA-z]", "", size)

        if unit == "B":
            return float(value) * 0.000001
        if unit == "K":
            return float(value)  * 0.001
        elif unit == "M":
            return float(value)
        elif unit == "G":
            return float(value) * 1000
        elif unit == "T":
            return float(value) * 1000000
        else:
            return None
    else:
        return None
# print size_in_mb("100.5M")

def read_fovs(file):
    data = np.genfromtxt(file, dtype=None, unpack=True, delimiter='\t')

    prev_vid = data[0][0]
    fovs = []
    idx = 0
    videos = []
    for d in data:
        vid = d[0]
        # print str(vid), str(prev_vid)
        if vid == prev_vid:
            # lat, lon, compass, R, alpha
            fov = FOV(data[idx][2],data[idx][3],data[idx][4],data[idx][5],data[idx][6])
            fovs.append(fov)
        else:
            # new video
            v = Video(fovs)
            v.id = prev_vid
            videos.append(v)
            # print v.to_str()

            # new fovs
            fovs = []
            fov = FOV(data[idx][2],data[idx][3],data[idx][4],data[idx][5],data[idx][6])
            fovs.append(fov)

        idx = idx + 1
        prev_vid = vid

    print "number of videos", len(videos)
    return videos



# Create geoq client api
geoq = sm.GeoqApi(sm.ApiClient(url))

# Returns a set of video locations in GEOJSON format (small sample data)
#geoq.sample_videos()

# Returns a set of video frames (of a particular video) in GEOJSON format (small sample data)
#geoq.sample_fovs()

# Create geoq client with API key
# Replace KEY_VALUE by actual one

geoq = sm.GeoqApi(sm.ApiClient(url, "X-API-KEY", "8b51UFM2SlBltx3s6864eUO1zSoefeK5"))



"""
Returns a set of video locations that are captured within a time interval (startdate -> enddate)
"""
def get_videos(swlat=34.018212, swlng=-118.291716, nelat=34.025296, nelng=-118.279826, startdate="2014-04-13 00:00:00", enddate="2016-04-13 23:59:59"):

#def get_videos(swlat=-90, swlng=-180, nelat=90, nelng=+180, startdate="2010-04-13 00:00:00", enddate="2017-04-13 23:59:59"):

    valid_fc_videos = [] # with video of size > 0

    if IS_FROM_MEDIAQ:
        fc_videos = geoq.rectangle_query(swlat, swlng, nelat, nelng)
        fc_videos = fc_videos.replace('None','null').replace('u\'','\"').replace('\'','\"')

        # print fc_videos

        # validate GEOJSON
        if VALIDATE_GEOJSON == True:
            geojson_validation = requests.post(validate_endpoint, data=fc_videos)
            if geojson_validation.json()['status'] != 'ok':
                print "Rectangle_query: Invalid geojson format"
                exit()

        fc_videos = geojson.loads(fc_videos)
        print "Number of videos: " + str(len(fc_videos.features))

        # fov_counts = []
        video_sizes = []
        for video in fc_videos.features:
            # fov_counts.append(video.properties['fov_count'])
            size = size_in_mb(video.properties['size'])
            if size and size > 0:
                print video
                valid_fc_videos.append(video)
                video_sizes.append(size)

        print "Total/Mean video size (M): " + str(sum(video_sizes)) + "/" + str(np.mean(video_sizes))
        bins = range(0,100,10)
        hist_video_counts = np.histogram(video_sizes, bins)[0]
        print "Histogram:" + str(hist_video_counts)

        # the histogram of the data
        plt.hist(video_sizes, bins=bins)
        plt.xlabel('Range (MB)')
        plt.ylabel('Video Count')
        plt.title(r'$\mathrm{Histogram\ of\ Video\ Size}$')
        # plt.axis([0, 100, 0, 500])
        plt.grid(True)
        # plt.show()

        # print "Total/Mean FOV count: " + str(sum(fov_counts)) + "/" + str(np.mean(fov_counts))
        # bins = range(0,200,20)
        # hist_fov_counts = np.histogram(fov_counts, bins)[0]
        # print "Histogram:" + str(hist_fov_counts)

        # the histogram of the data
        # plt.hist(fov_counts, bins=bins)
        # plt.xlabel('Range (Number of Frames)')
        # plt.ylabel('Frame Count')
        # plt.title(r'$\mathrm{Histogram\ of\ Frame\ Count}$')
        # plt.axis([0, 100, 0, 500])
        plt.grid(True)
        # plt.show()

    else:
        valid_fc_videos = read_fovs(VIDEO_FILE)

    return valid_fc_videos


def getFOVs(vid):
    fovs = []
    # Returns a set of video frames
    try:
        fovs = geoq.video_metadata(vid).replace('None','null').replace('u\'','\"').replace('\'','\"')
        if VALIDATE_GEOJSON == True:
            geojson_validation = requests.post(validate_endpoint, data=fovs)
            if geojson_validation.json()['status'] != 'ok':
                print "Video_metadata: Invalid geojson format"
        fovs = geojson.loads(fovs)
    except Exception as inst:
        print vid
        print inst
        print "Unexpected error:", sys.exc_info()[0]

    return fovs


"""
Shannon entropy a list of frequencies
"""
def shanon_entropy_list(l):
    if len(l) == 1:
        return 0
    total = 0
    s = sum(l)
    for v in l:
        c = float(v) / s
        total = total - c * np.log(c)
    return total


"""
Compute coverage map (2D histogram)
"""
def compute_coverage_map(grid_size = 100):
    swlat=34.018212
    swlng=-118.291716
    nelat=34.025296
    nelng=-118.279826
    videos = get_videos(swlat, swlng, nelat, nelng)

    map = np.ndarray(shape=(grid_size, grid_size), dtype=int)
    for video in videos:
        if IS_FROM_MEDIAQ:
            if video.properties['vid']:
                vid = str(video.properties['vid'])
                fovs = getFOVs(vid)

                if fovs and len(fovs) > 0:
                    for fov in fovs.features:
                        f = FOV(fov)
                        param = Params(200, swlat, swlng, nelat, nelng)
                        param.GRID_SIZE = grid_size
                        for cid in f.cellids(param):
                            cell_lat, cell_lng = cell_coord(cid, param)
                            if f.cover(cell_lat, cell_lng):
                                y_idx = cid/param.GRID_SIZE
                                x_idx = cid - y_idx*param.GRID_SIZE
                                # print x_idx, y_idx, map[x_idx][y_idx]
                                map[x_idx][y_idx] = map[x_idx][y_idx] + 1
        else:
            for f in video.fovs:
                param = Params(200, swlat, swlng, nelat, nelng)
                param.GRID_SIZE = grid_size
                for cid in f.cellids(param):
                    cell_lat, cell_lng = cell_coord(cid, param)
                    if f.cover(cell_lat, cell_lng):
                        y_idx = cid/param.GRID_SIZE
                        x_idx = cid - y_idx*param.GRID_SIZE
                        # print x_idx, y_idx, map[x_idx][y_idx]
                        map[x_idx][y_idx] = map[x_idx][y_idx] + 1

    fig, ax = plt.subplots()
    heatmap = ax.pcolor(map, cmap=plt.cm.Reds)
    plt.show()
    plt.close()
    np.savetxt("mediaq_coverage_heatmap.txt" , map, fmt='%i\t')


compute_coverage_map()