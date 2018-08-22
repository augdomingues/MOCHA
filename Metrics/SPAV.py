from Metrics.Metric import Metric
import math
import random

class SPAV(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.spav = {}
        self.venues = {}
        self.usersVenues = {}
        self.locations = {}
        self.infile = infile
        self.outfile = outfile
        self.locationsIndex = 0
        self.reportID = reportID
        self.r = kwargs.get("radius")
        self.maxX = 0
        self.maxY = 0
        self.maxT = 0

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.usersVenues.items():
                if self.reportID:
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
    def extractLocations(self):
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


    def collectMaxes(self):
        with open(self.infile) as inn:
            for line in inn:
                comps = line.strip().split(" ")
                time = float(comps[3])
                user1X = float(comps[5])
                user1Y = float(comps[6])
                user2X = float(comps[7])
                user2Y = float(comps[8])

                self.maxX = math.ceil(max(user1X, user2X, self.maxX))
                self.maxY = math.ceil(max(user1Y, user2Y, self.maxY))
                self.maxT = max(time, self.maxT)

    @Metric.timeexecution
    def extractVenues(self):
        self.extractLocations()
        self.collectMaxes()
        numberVenues = int(self.maxX * self.maxY / (self.r * self.r))
        numberVenues = min(835, numberVenues)

        keys = list(self.locations.keys())
        randomIndex = 0
        venuesIndex = 0

        for i in range(0, numberVenues):
            randomIndex = random.randint(0, len(keys) - 1)
            while keys[randomIndex] not in self.locations:
                randomIndex = random.randint(0, len(keys) - 1)
            self.venues[venuesIndex] = keys[randomIndex]
            venuesIndex += 1


    def euclidean(self, x, y):
        return math.sqrt(sum([(a - b) ** 2 for a, b in zip(x, y)]))

    @Metric.timeexecution
    def extract(self):
        self.extractVenues()
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
                    dist = self.euclidean((user1X, user1Y), (venX, venY))

                    if dist < distanceToCloser1:
                        distanceToCloser1 = dist
                        user1Venue = i

                    dist = self.euclidean((user1X, user1Y), (venX, venY))

                    if dist < distanceToCloser2:
                        distanceToCloser2 = dist
                        user2Venue = i

                if user1 in self.usersVenues:
                    value = self.usersVenues[user1].get(user1Venue, 0)
                    self.usersVenues[user1][user1Venue] = value + 1
                else:
                    self.usersVenues[user1] = {}

                if user2 in self.usersVenues:
                    value = self.usersVenues[user2].get(user2Venue, 0)
                    self.usersVenues[user2][user2Venue] = value + 1
                else:
                    self.usersVenues[user2] = {}


        for key, item in self.usersVenues.items():
            summ = sum([v for v in item.values()])
            summ = max(summ, 1)
            entropy = 0
            for v in item.values():
                entropy += (v/summ) * math.log2((1/(v/summ)))
            self.usersVenues[key] = entropy


    def commit(self):
        values = {"venues": self.venues, "locations": self.locations,
                  "maxX": self.maxX, "maxY": self.maxY, "maxT": self.maxT}
        return values
