"""
    This module extracts the Visit Time (VIST) metric for each node
    in the trace.
"""
import math
from Metrics.Metric import Metric


class VIST(Metric):
    """ VIST extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.vist = {}
        self.venues = {}
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id
        self.venues = kwargs["venues"]
        self.locations = kwargs["locations"]

        # Get the cached locations
        self.cache_locations = kwargs["cache_locations"]

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.vist.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    def euclidean(self, xval, yval):
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(xval, yval)]))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")

                user1, user2 = comps[0], comps[1]
                user1_x, user1_y = float(comps[5]), float(comps[6])
                user2_x, user2_y = float(comps[7]), float(comps[8])

                time = float(comps[4])

                distance_to_closer1 = distance_to_closer2 = math.inf
                user1_venue = user2_venue = -1

                # Get the cached location
                key1 = "{} {}".format(user1_x, user1_y)
                key2 = "{} {}".format(user2_x, user2_y)

                cache1 = key1 in self.cache_locations
                cache2 = key2 in self.cache_locations

                if cache1:
                    user1_venue = self.cache_locations[key1]
                if cache2:
                    user2_venue = self.cache_locations[key2]

                if not cache1 or not cache2:
                    for i in range(0, len(self.venues)):
                        vx, vy = [float(c) for c in self.venues[i].split(" ")]

                        if not cache1:
                            dist = self.euclidean((user1_x, user1_y), (vx, vy))
                            if dist < distance_to_closer1:
                                distance_to_closer1 = dist
                                user1_venue = i

                        if not cache2:
                            dist = self.euclidean((user2_x, user2_y), (vx, vy))
                            if dist < distance_to_closer2:
                                distance_to_closer2 = dist
                                user2_venue = i

                    self.cache_locations[key1] = user1_venue
                    self.cache_locations[key2] = user2_venue

                if user1 in self.vist:
                    visit_time = self.vist[user1].get(user1_venue, 0.0)
                    self.vist[user1][user1_venue] = visit_time + time
                else:
                    self.vist[user1] = {}

                if user2 in self.vist:
                    visit_time = self.vist[user2].get(user2_venue, 0.0)
                    self.vist[user2][user2_venue] = visit_time + time
                else:
                    self.vist[user2] = {}

        for key, item in self.vist.items():
            vistd = sum(item.values())
            vistd = vistd/max(len(item), 1)
            self.vist[key] = vistd

    def commit(self):
        return {}

    def explain(self):
        return "VIST"
