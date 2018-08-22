from Metrics.Metric import Metric
from Home import Home
import math


class RADG(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.infile = infile
        self.outfile = outfile
        self.userHomes = {}
        self.radius = {}
        self.reportID = reportID
        self.venues = kwargs.get("venues")

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.radius.items():
                if self.reportID:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    def explain(self):
        return "RADG"

    def getClosestVenue(self, x, y):
        minimum = math.inf
        closest = 0

        for k, item in self.venues.items():
            venueLocX, venueLocY = item.split(" ")
            distance = self.euclidean((x, y), (venueLocX, venueLocY))

            if distance < minimum:
                minimum = distance
                closest = k

        return self.venues[closest]

    def euclidean(self, x, y):
        e = sum([(float(a) - float(b)) ** 2 for a, b in zip(x, y)])
        e = math.sqrt(e)
        return e

    @Metric.timeexecution
    def extractHome(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1 = comps[0]
                user1X, user1Y = comps[5], comps[6]
                user1Location = self.getClosestVenue(user1X, user1Y)

                if user1 not in self.userHomes:
                    self.userHomes[user1] = Home(user1Location, 1)
                else:
                    location = self.userHomes[user1].location
                    degree = self.userHomes[user1].degree
                    if location == user1Location:
                        self.userHomes[user1].degree += 1
                    elif degree == 0:
                        self.userHomes[user1] = Home(user1Location, 1)
                    else:
                        self.userHomes[user1].degree -= 1

                user2 = comps[1]
                user2X, user2Y = comps[7], comps[8]
                user2Location = self.getClosestVenue(user2X, user2Y)

                if user2 not in self.userHomes:
                    self.userHomes[user2] = Home(user2Location, 1)
                else:
                    location = self.userHomes[user2].location
                    degree = self.userHomes[user2].degree
                    if location == user2Location:
                        self.userHomes[user2].degree += 1
                    elif degree == 0:
                        self.userHomes[user2] = Home(user2Location, 1)
                    else:
                        self.userHomes[user2].degree -= 1

    @Metric.timeexecution
    def extract(self):
        self.extractHome()
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]

                user1X, user1Y = comps[5], comps[6]
                user2X, user2Y = comps[7], comps[8]

                user1Home = self.userHomes[user1].location
                user1HomeX, user1HomeY = user1Home.split(" ")
                user2Home = self.userHomes[user2].location
                user2HomeX, user2HomeY = user1Home.split(" ")

                user1Dist = self.euclidean((user1X, user1Y), (user1HomeX,
                                           user1HomeY))

                user2Dist = self.euclidean((user2X, user2Y), (user2HomeX,
                                           user2HomeY))

                currentValue = self.radius.get(user1, 0)
                self.radius[user1] = max(currentValue, user1Dist)

                currentValue = self.radius.get(user2, 0)
                self.radius[user2] = max(currentValue, user2Dist)


    def commit(self):
        return {}
