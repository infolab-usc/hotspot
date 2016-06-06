__author__ = 'ubriela'

from matplotlib import pyplot
from shapely.geometry import Polygon
from descartes import PolygonPatch
from shapely.ops import cascaded_union

from Utils import rect_area
from FOV import FOV

from UtilsBDR import *

class Video(object):

    id = 0
    value = 0
    size = 0
    fov_count = 0

    def __init__(self):
        self.fovs = None    # list of FOVs

    def __init__(self, fovs):
        self.fovs = fovs

    def get_fovs(self):
        return self.fovs[0:self.fov_count]

    def c_union(self):
        if self.fovs is not None:
            polygons = [Polygon(mbr_to_path(fov.mbr())) for fov in self.fovs[0:self.fov_count]]
            u = cascaded_union(polygons)
            return u
        else:
            print None

    def area(self):
        if self.fovs is not None:
            return self.c_union().area / (1000000*Params.ONE_KM*Params.ONE_KM)
        else:
            print 'No FOV!'
            return 0

    """
    view point of the first FOV
    """
    def location(self):
        return [self.fovs[0].lat, self.fovs[0].lon]

    def sum_fov_area(self):
        return sum([fov.area() for fov in self.fovs])

    def to_str(self):
        return str(self.id) + "\n" + "\n".join(fov.to_str() for fov in self.fovs)



