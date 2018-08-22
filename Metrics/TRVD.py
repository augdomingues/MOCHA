from Metrics.Metric import Metric
import math
from TravelPair import TravelPair

class TRVD(Metric):

    def __init__(self, infile, outfile, reportID, **kwargs):
        self.trvd = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID
        self.kwargs = kwargs

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.trvd.items():
                if self.reportID:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    def euclidean(self, x, y):
        return math.sqrt(sum([(float(a) - float(b)) ** 2 for a, b in zip(x, y)]))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]

                user1X, user1Y = comps[5], comps[6]

                user2X, user2Y = comps[7], comps[8]

                if user1 in self.trvd:
                    curr = self.trvd[user1][-1].location
                    currX, currY = curr.split(" ")

                    distance = self.euclidean((user1X, user1Y), (currX, currY))

                    tp = TravelPair(user1X + " " + user1Y, distance)
                    self.trvd[user1].append(tp)
                else:
                    tp = TravelPair(user1X + " " + user1Y, 0.0)
                    self.trvd[user1] = [tp]

                if user2 in self.trvd:
                    curr = self.trvd[user2][-1].location
                    currX, currY = curr.split(" ")

                    distance = self.euclidean((user2X, user2Y), (currX, currY))

                    tp = TravelPair(user2X + " " + user2Y, distance)
                else:
                    tp = TravelPair(user2X + " " + user2Y, 0.0)
                    self.trvd[user2] = [tp]

        for key, item in self.trvd.items():
            total = sum([t.distance for t in item])
            total = total/max(len(item), 1)
            self.trvd[key] = total

    def commit(self):
        return {}

    def explain(self):
        return "TRVD"

