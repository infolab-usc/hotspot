# Basic parameters
class Params(object):
    DATASET = "mediaq"

    NDATA = None
    NDIM = None
    LOW = None
    HIGH = None
    nQuery = 2  # number of queries
    unitGrid = 0.01  # cell unit in kd-cell
    ONE_KM = 0.0089982311916  # convert km to degree
    ZIPFIAN_SKEW = 2
    URGENCY_RANDOM = True

    POPULATION_FILE = '../../dataset/gowalla_CA.dat'

    # for grid standard
    # maxHeight = 2
    # part_size = 6
    # ANALYST_COUNT = 36

    part_size = 8
    ANALYST_COUNT = 256

    GRID_SIZE = 200

    def __init__(self, seed, x_min = None, y_min = None, x_max = None, y_max = None):
        self.Seed = seed
        self.minPartSize = 2 ** 0  # maximum number of data points in a leaf node

        self.resdir = ""
        self.x_min, self.y_min, self.x_max, self.y_max = x_min, y_min, x_max, y_max
        self.NDATA = None
        self.NDIM = None
        self.LOW = None
        self.HIGH = None

    def debug(self):
        print self.x_min, self.y_min, self.x_max, self.y_max
        print self.NDATA, self.NDIM, self.LOW, self.HIGH

    def select_dataset(self):
        if Params.DATASET == "mediaq":
            self.dataset = 'FOVMetadata.txt'
            self.resdir = '../../output/mediaq/'
            self.x_min = 34.018212
            self.y_min = -118.291716
            self.x_max = 34.025296
            self.y_max = -118.279826