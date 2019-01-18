from random import randrange, randint
from math import radians, sin, cos
from collections import namedtuple


class Coords(namedtuple('Coords', ['x', 'y'])):

    __slots__ = ()
    
    '''
    def __init__(self, x, y, round_co=True):
        """A class for storing two interiger or float values for use in a Cartesian coordinate system."""
        if round_co:
            self.x = round(x)
            self.y = round(y)
        else:
            self.x = x
            self.y = y
    '''

    '''
    @property
    def x(self):
        return self.x

    @property
    def y(self):
        return self.y
    '''
    @classmethod
    def new_coords(cls, x, y, round_co=True):
        if round_co:
            return cls(round(x), round(y))
        else:
            return cls(x, y)

    @classmethod
    def random_positive_coords(cls, x, y):
        return cls(randrange(0, x), randrange(0, y))

    @classmethod
    def from_tuple(cls, x, y):
        return cls(x, y)

    @property
    def round(self):
        return Coords(round(self.x), round(self.y))

    @property
    def tup(self):
        return self.x, self.y

    def __str__(self):
        return 'X: {}, Y: {}'.format(self.x, self.y)

    def clamp(self, x, y):
        """Returns a Coords object with is x and y values clamped between zero and the parameter that is passed in."""
        return Coords(max(min(self.x, x - 1), 0), max(min(self.y, y - 1), 0))

    def __sub__(self, coords):
        try:
            return Coords(self.x - coords.x, self.y - coords.y)
        except AttributeError:
            return Coords(self.x - coords[0], self.y - coords[1])

    def __add__(self, coords):
        try:
            return Coords(self.x + coords.x, self.y + coords.y)
        except AttributeError:
            return Coords(self.x + coords[0], self.y + coords[1])

    def __mul__(self, value):
        return Coords(round(self.x * value), round(self.y * value))

    def __div__(self, value):
        return Coords(round(self.x / value), round(self.y / value))

    def check(self, x, y):
        return self.x == x and self.y == y

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.x, self.y))

    def distance(self, cooards_x, cooards_y=None):
        if cooards_y is None:
            return pow((pow(self.x - cooards_x.x, 2) + pow(self.y - cooards_x.y, 2)), 0.5)
        return pow((pow(self.x - cooards_x, 2) + pow(self.y - cooards_y, 2)), 0.5)

    def check_if_is_in_range(self, xRangeEnd, yRangeEnd, xRangeStart=0, yRangeStart=0):
        """Retruns true if the Coords objects x value is """
        return self.x in range(xRangeStart, xRangeEnd) and self.y in range(yRangeStart, yRangeEnd)

    def clone(self):
        """Returns a shalow copy of this Coords object."""
        return Coords(self.x, self.y)

    @staticmethod
    def distance_static(x1, x2, y1=None, y2=None):

        if y1 is None or y2 is None:
            return x1.distance(x2)
        else:
            return pow((pow(x1 - x2, 2) + pow(y1 - y2, 2)), 0.5)

    def normalize(self, x=None, y=None, new_tuple=True, round_to=False):

        if x is None and y is None:
            x = self.x
            y = self.y
        elif y is None:
            x, y = x.x, x.y
        d = pow(pow(x, 2) + pow(y, 2), 0.5)
        try:
            nX = x / d
        except ZeroDivisionError:
            nX = 0
        try:
            nY = y / d
        except ZeroDivisionError:
            nY = 0

        if new_tuple:
            if round_to:
                return round(nX), round(nY)
            else:
                return nX, nY
        else:
            return Coords.new_coords(nX, nY, round_co=round_to)

    @property
    def is_diagonal(self):
        return self.x != 0 and self.y != 0

    @property
    def is_horizontal(self):
        return self.x != 0 and self.y == 0

    @property
    def is_vertical(self):
        return self.x == 0 and self.y != 0

    def is_adjacent(self, coords):
        return self.x in range(coords.x - 1, coords.x + 1) and self.y in range(coords.y - 1, coords.y + 1)

    @classmethod
    def random_point_within_radius(cls, radius):
        """Returns a random point from within the specified radius."""

        x = randint(-radius, radius+1)
        y = randint(-radius, radius+1)

        d = pow((pow(x, 2) + pow(y, 2)), 0.5)

        if d == 0:
            return cls(0, 0)
        else:
            return cls(round(((x / d) * radius)), round((y / d) * radius))


DIR_UP =            Coords(0, -1)
DIR_UP_RIGHT =      Coords(1, -1)
DIR_RIGHT =         Coords(1, 0)
DIR_DOWN_RIGHT =    Coords(1, 1)
DIR_DOWN =          Coords(0, 1)
DIR_DOWN_LEFT =     Coords(-1, 1)
DIR_LEFT =          Coords(-1, 0)
DIR_UP_LEFT =       Coords(-1, -1)
DIR_CENTER =        Coords(0, 0)

ALL_DIRECTIONS = (DIR_UP, DIR_UP_RIGHT, DIR_RIGHT, DIR_DOWN_RIGHT, DIR_DOWN, DIR_DOWN_LEFT, DIR_LEFT, DIR_UP_LEFT, DIR_CENTER)
NO_CENTER = (DIR_UP, DIR_UP_RIGHT, DIR_RIGHT, DIR_DOWN_RIGHT, DIR_DOWN, DIR_DOWN_LEFT, DIR_LEFT, DIR_UP_LEFT)


def rotate_point(x, y, degrees, use_tuple=True):
    co = Coords.new_coords(x, y, round_co=False)
    dist = DIR_CENTER.distance(co)
    n_x, n_y = co.normalize()

    rads = radians(degrees)
    s_rads = sin(rads)
    c_rads = cos(rads)

    x2 = n_x * c_rads - n_y * s_rads
    y2 = n_y * s_rads - n_x * c_rads

    if use_tuple:

        return dist * x2, dist * y2
    else:
        return Coords.new_coords(dist * x2, dist * y2, round_co=False)

def angle_to_point(degrees, distance=1.0):
    rads = radians(degrees)

    return Coords(sin(rads) * distance, cos(rads) * distance)

check_increment = lambda x: -1 if x < 0 else 1

def rounded_ranges(coord1, coord2):

    diffrence_coord = coord2 - coord1

    if abs(diffrence_coord.x) > abs(diffrence_coord.y):
        # if the defualt x range will have a bigger length then the defualt y range

        # assume that coord1.x is 6
        # coord1.y is 4
        # coord2.x is 15
        # coord2.y is 7
        # therefore:
        # diffrence_coord is 9
        # diffrence_coord is 3

        x_gen = (x for x in range(coord1.x, coord2.x, check_increment(diffrence_coord.x)))
        # check_increment returns 1
        # 6, 7, 8, 9, 10, 11, 12, 13, 14

        # what we want is:
        # x: 6, 7, 8, 9, 10, 11, 12, 13, 14
        # y: 4, 4, 4, 5, 5,  5,  6,  6,  6

        fract = diffrence_coord.y / diffrence_coord.x
        # assume that fract is 0.333...

        y_gen = (coord1.y + round(fract * f) for f in range(coord1.y, coord1.y + diffrence_coord.y))
        #
        #
        #

        x_range = range(coord1.x, coord2.x, check_increment(diffrence_coord.x))

        y_range = range(coord1.y, coord2.y, check_increment(diffrence_coord.x))

    cx, cy = coord.normalize(new_tuple=True)