class Encounter:
    """ Represents an encounter between two nodes. """

    def __init__(self, id1, id2):
        self.id1 = int(id1)
        self.id2 = int(id2)

    def toString(self):
        """ Returns the encounter as a string. """
        if self.id1 < self.id2:
            return str(self.id1) + " " + str(self.id2)
        else:
            return str(self.id2) + " " + str(self.id1)
