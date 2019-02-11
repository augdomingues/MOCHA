"""
    This module extracts the Radius of Gyration (RADG) metric for each
    node in the trace.
"""
import math
from Metrics.Metric import Metric
from mocha_utils import Home


class RADG(Metric):
    """ RADG extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.infile = infile
        self.outfile = outfile
        self.user_homes = {}
        self.radius = {}
        self.report_id = report_id
        self.venues = kwargs.get("venues")

        # Get the cached locations
        self.cache_locations = kwargs.get("cache_locations")

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.radius.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    def explain(self):
        return "RADG"

    def get_closest_venue(self, x, y):
        """ Returns the closest venue to a point. """
        minimum = math.inf
        closest = 0

        for k, item in self.venues.items():
            vx, vy = item.split(" ")
            distance = self.euclidean((x, y), (vx, vy))

            if distance < minimum:
                minimum = distance
                closest = k

        return self.venues[closest]

    def euclidean(self, x, y):
        """ Returns the euclidean distance between two points. """
        euclidean = sum([(float(a) - float(b)) ** 2 for a, b in zip(x, y)])
        euclidean = math.sqrt(euclidean)
        return euclidean

    @Metric.timeexecution
    def extract_home(self):
        """ Finds the home of a user. """
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1 = comps[0]
                user1X, user1Y = comps[5], comps[6]

                # Check the user position in the cached locations
                key1 = "{} {}".format(user1X, user1Y)
                if key1 in self.cache_locations:
                    user1Location = self.cache_locations[key1]
                    user1Location = self.venues[user1Location]
                else:
                    user1Location = self.get_closest_venue(user1X, user1Y)

                if user1 not in self.user_homes:
                    self.user_homes[user1] = Home(user1Location, 1)
                else:
                    location = self.user_homes[user1].location
                    degree = self.user_homes[user1].degree
                    if location == user1Location:
                        self.user_homes[user1].degree += 1
                    elif degree == 0:
                        self.user_homes[user1] = Home(user1Location, 1)
                    else:
                        self.user_homes[user1].degree -= 1

                user2 = comps[1]
                user2X, user2Y = comps[7], comps[8]

                # Check user2 position in the cached locations
                key2 = "{} {}".format(user2X, user2Y)
                if key2 in self.cache_locations:
                    user2Location = self.cache_locations[key2]
                    user2Location = self.venues[user2Location]
                else:
                    user2Location = self.get_closest_venue(user2X, user2Y)

                if user2 not in self.user_homes:
                    self.user_homes[user2] = Home(user2Location, 1)
                else:
                    location = self.user_homes[user2].location
                    degree = self.user_homes[user2].degree
                    if location == user2Location:
                        self.user_homes[user2].degree += 1
                    elif degree == 0:
                        self.user_homes[user2] = Home(user2Location, 1)
                    else:
                        self.user_homes[user2].degree -= 1

    @Metric.timeexecution
    def extract(self):
        self.extract_home()
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]

                user1_X, user1_Y = comps[5], comps[6]
                user2_X, user2_Y = comps[7], comps[8]

                user1_Home = self.user_homes[user1].location
                user1_HomeX, user1_HomeY = user1_Home.split(" ")
                user2_Home = self.user_homes[user2].location
                user2_HomeX, user2_HomeY = user2_Home.split(" ")

                user1_Dist = self.euclidean((user1_X, user1_Y), (user1_HomeX,
                                            user1_HomeY))

                user2_Dist = self.euclidean((user2_X, user2_Y), (user2_HomeX,
                                            user2_HomeY))

                currentValue = self.radius.get(user1, 0)
                self.radius[user1] = max(currentValue, user1_Dist)

                currentValue = self.radius.get(user2, 0)
                self.radius[user2] = max(currentValue, user2_Dist)

    def commit(self):
        return {}
