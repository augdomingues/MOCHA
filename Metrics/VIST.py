from Metrics.Metric import Metric
import math

class VIST(Metric):

    def __init__(self, infile, outfile, reportID, **kwargs):
        self.vist = {}
        self.venues = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID
        self.venues = kwargs["venues"]
        self.locations = kwargs["locations"]

        #Get the cached locations
        self.cache_locations = kwargs["cache_locations"]

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.vist.items():
                if self.reportID:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))


    def euclidean(self, x, y):
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")

                user1, user2 = comps[0], comps[1]
                user1X, user1Y = float(comps[5]), float(comps[6])
                user2X, user2Y = float(comps[7]), float(comps[8])

                time = float(comps[4])

                distanceToCloser1 = distanceToCloser2 = math.inf
                user1Venue = user2Venue = -1

                # Get the cached location
                key1 = "{} {}".format(user1X, user1Y)
                key2 = "{} {}".format(user2X, user2Y)

                cache1 = key1 in self.cache_locations
                cache2 = key2 in self.cache_locations

                if cache1:
                    user1Venue = self.cache_locations[key1]
                if cache2:
                    user2Venue = self.cache_locations[key2]

                if not cache1 or not cache2:
                    for i in range(0, len(self.venues)):
                        vx, vy = [float(c) for c in self.venues[i].split(" ")]

                        if not cache1:
                            dist = self.euclidean((user1X, user1Y), (vx, vy))
                            if dist < distanceToCloser1:
                                distanceToCloser1 = dist
                                user1Venue = i

                        if not cache2:
                            dist = self.euclidean((user2X, user2Y), (vx, vy))
                            if dist < distanceToCloser2:
                                distanceToCloser2 = dist
                                user2Venue = i

                    self.cache_locations[key1] = user1Venue
                    self.cache_locations[key2] = user2Venue


                if user1 in self.vist:
                    visitTime = self.vist[user1].get(user1Venue, 0.0)
                    self.vist[user1][user1Venue] = visitTime + time
                else:
                    self.vist[user1] = {}

                if user2 in self.vist:
                    visitTime = self.vist[user2].get(user2Venue, 0.0)
                    self.vist[user2][user2Venue] = visitTime + time
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
