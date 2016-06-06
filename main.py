__author__ = 'minh'
from FOV import FOV
from Video import Video
import numpy as np


def read_data(file):
    data = np.genfromtxt(file, unpack=True, delimiter = '\t')

    prev_vid = 1
    fovs = []
    idx = 0
    videos = []
    for vid in data[1]:
        if vid == prev_vid:
            #lat, long, compass, R, alpha
            fov = FOV(data[2][idx], data[3][idx], data[4][idx], data[5][idx], data[6][idx])
            fovs.append(fov)
        else:
            # new video
            v = Video(fovs)
            v.id = vid
            videos.append(v)
            # print v.to_str()

            # new fovs
            fovs = []
            fov = FOV(data[2][idx], data[3][idx], data[4][idx], data[5][idx], data[6][idx])
            fovs.append(fov)

        idx += 1
        prev_vid = vid

    return videos



print read_data("FOVMetadata.txt")
