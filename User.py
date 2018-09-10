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
