class Cell:
    """ Represents a cell where nodes can be within. """

    def __init__(self, k, l):
        self.k = k
        self.l = l

    def __eq__(self, other):
        if self.k == other.k and self.l == other.l:
            return 0
        return 1

    def __str__(self):
        return "{} {}".format(self.k, self.l)

class PositionReport:
    def __init__(self, x, y, t):
        self.x, self.y, self.t = x, y ,y

    def euclidean(self, xj, yj):
        e = ((self.x - xj) ** 2) + ((self.y - yj) **2)
        e = e**(1/2)
        return e

    def __sub__(self, other):
        return self.euclidean(other.x , other.y)


class Encounter:
    """ Represents an encounter between two nodes. """

    def __init__(self, id1, id2):
        self.id1 = int(id1)
        self.id2 = int(id2)

    def __str__(self):
        """ Returns the encounter as a string. """
        higher = max(self.id1, self.id2)
        lower = min(self.id1, self.id2)

        return "{} {}".format(higher, lower)

class Home:
    """ Represents an node (e.g. a user) home location """

    def __init__(self, l, d):
        self.location = l
        self.degree = d

class Location:
    """ Represents a node (e.g. a user) current location. """

    def __init__(self, l, vt):
        self.location = l
        self.visitTime = vt

class PositionEntry:

    def __init__(self, positionX, positionY, coordX, coordY, time):
        self.positionX = positionX
        self.positionY = positionY
        self.coordX = coordX
        self.coordY = coordY
        self.time = time

class TravelPair:
    """ Represents a travel made by a user. """

    def __init__(self, string, distance):
        self.distance = distance
        self.location = string

class User:
    """ Represents a user in the trace. """

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def __eq__(self, other):
        if self.id == other.id and self.x == other.x and self.y == other.y:
            return 0
        return 1

    def __str__(self):
        return "{}".format(self.id)

