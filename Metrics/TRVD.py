"""
    This module extracts the Travel Distance (TRVD) metric for
    each node in the trace.
"""
import math
from Metrics.Metric import Metric
from mocha_utils import TravelPair


class TRVD(Metric):
    """ TRVD extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.trvd = {}
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id
        self.kwargs = kwargs

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.trvd.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    def euclidean(self, x, y):
        """ Computes the euclidean distance between two points. """
        return math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(x, y)))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]

                user1_x, user1_y = comps[5], comps[6]

                user2_x, user2_y = comps[7], comps[8]

                if user1 in self.trvd:
                    curr = self.trvd[user1][-1].location
                    curr_x, curr_y = curr.split(" ")

                    distance = self.euclidean((user1_x, user1_y),
                                              (curr_x, curr_y))

                    travel_pair = TravelPair(user1_x + " " + user1_y, distance)
                    self.trvd[user1].append(travel_pair)
                else:
                    travel_pair = TravelPair(user1_x + " " + user1_y, 0.0)
                    self.trvd[user1] = [travel_pair]

                if user2 in self.trvd:
                    curr = self.trvd[user2][-1].location
                    curr_x, curr_y = curr.split(" ")

                    distance = self.euclidean((user2_x, user2_y),
                                              (curr_x, curr_y))

                    travel_pair = TravelPair(user2_x + " " + user2_y, distance)
                else:
                    travel_pair = TravelPair(user2_x + " " + user2_y, 0.0)
                    self.trvd[user2] = [travel_pair]

        for key, item in self.trvd.items():
            total = sum([t.distance for t in item])
            total = total/max(len(item), 1)
            self.trvd[key] = total

    def commit(self):
        return {}

    def explain(self):
        return "TRVD"
