"""
    This module extracts the Spatial variability (SPAV) metric for each node
    in the trace.
"""
import math
import random
from Metrics.Metric import Metric


class SPAV(Metric):
    """ SPAV extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.spav = {}
        self.venues = {}
        self.users_venues = {}
        self.locations = {}
        self.infile = infile
        self.outfile = outfile
        self.locationsIndex = 0
        self.report_id = report_id
        self.r = kwargs.get("radius")
        self.max_x = 0
        self.max_y = 0
        self.max_t = 0

        self.cache_locations = {}

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.users_venues.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    def explain(self):
        strg = """

            SPAV - Spatial Variability
            .
            .
            .

        """
        return strg

    @Metric.timeexecution
    def extract_locations(self):
        """ Extract all the locations in the trace. """
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                key = "{} {}".format(comps[5], comps[6])

                if key not in self.locations:
                    self.locations[key] = self.locationsIndex
                    self.locationsIndex += 1

                key = "{} {}".format(comps[7], comps[8])

                if key not in self.locations:
                    self.locations[key] = self.locationsIndex
                    self.locationsIndex += 1

    def collect_maxes(self):
        """ Extract max values from the trace. """
        with open(self.infile) as inn:
            for line in inn:
                comps = line.strip().split(" ")
                time = float(comps[3])
                user1_x = float(comps[5])
                user1_y = float(comps[6])
                user2_x = float(comps[7])
                user2_y = float(comps[8])

                self.max_x = math.ceil(max(user1_x, user2_x, self.max_x))
                self.max_y = math.ceil(max(user1_y, user2_y, self.max_y))
                self.max_t = max(time, self.max_t)

    @Metric.timeexecution
    def extract_venues(self):
        """ Extract the venues in the trace. """
        self.extract_locations()
        self.collect_maxes()
        number_venues = int(self.max_x * self.max_y / (self.r * self.r))
        number_venues = min(835, number_venues)

        keys = list(self.locations.keys())
        random_index = 0
        venues_index = 0

        for _ in range(0, number_venues):
            random_index = random.randint(0, len(keys) - 1)
            while keys[random_index] not in self.locations:
                random_index = random.randint(0, len(keys) - 1)
            self.venues[venues_index] = keys[random_index]
            venues_index += 1

    def euclidean(self, x, y):
        """ Computes the euclidean distance. """
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))

    @Metric.timeexecution
    def extract(self):
        self.extract_venues()
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]
                user_1x, user_1y = float(comps[5]), float(comps[6])
                user_2x, user_2y = float(comps[7]), float(comps[8])

                distance_to_closer1 = distance_to_closer2 = math.inf
                user1_venue = user2_venue = -1

                # Set the keys as the locations
                key1 = "{} {}".format(user_1x, user_1y)
                key2 = "{} {}".format(user_2x, user_2y)
                # Check if any of the keys are in the locations cache
                # If so, use the cached location
                cached1 = key1 in self.cache_locations
                cached2 = key2 in self.cache_locations
                if cached1:
                    user1_venue = self.cache_locations[key1]
                if cached2:
                    user2_venue = self.cache_locations[key2]

                if not cached1 or not cached2:
                    for i in range(0, len(self.venues)):

                        vx, vy = [float(c) for c in self.venues[i].split(" ")]

                        if not cached1:
                            dist = self.euclidean((user_1x, user_1y), (vx, vy))
                            if dist < distance_to_closer1:
                                distance_to_closer1 = dist
                                user1_venue = i

                        if not cached2:
                            dist = self.euclidean((user_2x, user_2y), (vx, vy))
                            if dist < distance_to_closer2:
                                distance_to_closer2 = dist
                                user2_venue = i

                    # Cache locations selected to users positions
                    self.cache_locations[key1] = user1_venue
                    self.cache_locations[key2] = user2_venue

                if user1 in self.users_venues:
                    value = self.users_venues[user1].get(user1_venue, 0)
                    self.users_venues[user1][user1_venue] = value + 1
                else:
                    self.users_venues[user1] = {}

                if user2 in self.users_venues:
                    value = self.users_venues[user2].get(user2_venue, 0)
                    self.users_venues[user2][user2_venue] = value + 1
                else:
                    self.users_venues[user2] = {}

        for key, item in self.users_venues.items():
            summ = sum([v for v in item.values()])
            summ = max(summ, 1)
            entropy = 0
            for v in item.values():
                entropy += (v/summ) * math.log2((1/(v/summ)))
            self.users_venues[key] = entropy

    def commit(self):
        values = {"venues": self.venues, "locations": self.locations,
                  "maxX": self.max_x, "maxY": self.max_y, "maxT": self.max_t,
                  "cache_locations": self.cache_locations}
        return values
