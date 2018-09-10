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
