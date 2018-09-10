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
