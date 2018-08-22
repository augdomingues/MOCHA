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
                user1Venue = user2Venue = 0

                for i in range(0, len(self.venues)):
                    venX, venY = [float(c) for c in self.venues[i].split(" ")]
                    dist = self.euclidean( (user1X, user1Y), (venX, venY))

                    if dist < distanceToCloser1:
                        distanceToCloser1 = dist
                        user1Venue = i

                    dist = self.euclidean( (user2X, user2Y), (venX, venY))

                    if dist < distanceToCloser2:
                        distanceToCloser2 = dist
                        user2Venue = i

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
