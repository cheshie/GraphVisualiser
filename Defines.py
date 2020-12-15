
LABEL_LEFT  = 0
LABEL_RIGHT = 1

BRIDGE_LEFT  = 0
BRIDGE_RIGHT = 1

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    # Get point from another point
    @classmethod
    def fromPoint(cls, point):
        # assert type(point) == type(Point)
        return cls(point.x, point.y)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        if isinstance(other, int):
            return Point(self.x + other, self.y + other)
    #

    def __str__(self):
        return str("(x: " + str(self.x) + " y: " + str(self.y) + ")")
#

class Bridge:
    def __init__(self, left_point, length=0, bridge_size=BRIDGE_RIGHT):
        self.left_point  = left_point
        self.right_point = left_point + Point(x=length)
        self.length      = length

    def __str__(self):
        return str("Left point: " + str(self.left_point) + " Right point: " + str(self.right_point))

    # Add Point() (offset) to a bridge's points
    def __add__(self, other):
        if isinstance(other, Point):
            return Bridge(self.left_point + other, self.length)