from Graph import Graph
from Graph import Vertex
from Graph import Edge
from Encounter import Encounter
from Location import Location
from Home import Home
from TravelPair import TravelPair
import sys
import math
import random
import os
from Bar import Bar
import pdb

class Extractor:

    def __init__(self, filename, maxTime, maxX, maxY, r, filesize,
                 metrics, report_id):

        # Checks if system is windows to create folder correctly
        self.barra = os.sep
        if "." in filename:
            self.folderName = filename.replace("_parsed.csv", "").replace("_parsed.txt", "")
            self.folderName += "_metrics_folder{}".format(self.barra)
        else:
            self.folderName = filename.replace("_parsed", "")
            self.folderName += "_metrics_folder{}".format(self.barra)

        self.file, self.filesize = filename, filesize
        self.generatedFileNames = {}
        self.maxX, self.maxY, self.r, self.maxTime = maxX, maxY, r, maxTime
        self.metrics = [key for key in metrics.keys()]

        # Guarantees that SOCOR is always the last element
        if "SOCOR" in self.metrics:
            self.metrics.remove("SOCOR")
            self.metrics.append("SOCOR")
        self.metricFiles = {}

        # Structures for the metrics
        self.inco = {}
        self.incoGraph = Graph()
        self.codu = {}
        self.maxcon = [0] * (int(self.maxTime/3600) + 1)
        self.edgep = {}
        self.encounters = {}
        self.topo = {}
        self.totalNeighbors = {}
        self.topoGraph = Graph()
        self.locations = {}
        self.locationsIndex = 0
        self.venues = {}
        self.usersVenues = {}
        self.usersContacts = {}
        self.userHomes = {}
        self.radius = {}
        self.trvd = {}
        self.vist = {}
        self.REPORT_ID = report_id

        if not os.path.exists(self.folderName):
            os.makedirs(self.folderName)
        with open("filesForFitting.txt", "w+") as fitting:
            for key in self.metrics:
                filename = "{}{}.txt".format(self.folderName, key)
                with open(filename, "w+") as saida:
                    pass
                fitting.write("{}\n".format(filename))
                self.metricFiles[key] = filename

    def printMetrics(self, metrics):
        functions = {"EDGEP": self.printEDGEP, "TOPO": self.printTOPO,
                     "RADG": self.printRADG, "TRVD": self.printTRVD,
                     "VIST": self.printVIST, "MAXCON": self.printMAXCON,
                     "SPAV": self.printSPAV, "CONEN": self.printCONEN}

        for m in metrics:
            if m in functions:
                functions[m]()

    def extractMetrics(self, metrics, line):
        functions = {"INCO": self.extractINCO, "CODU": self.extractCODU,
                     "MAXCON": self.extractMAXCON, "EDGEP": self.extractEDGEP,
                     "TOPO": self.extractTOPO, "TRVD": self.extractTRVD,
                     "RADG": self.extractRADG}

        for m in metrics:
            if m in functions:
                functions[m](line)

    def extract(self):
        self.extractLocations()
        self.extractVenues()
        self.voronoi()
        bar = Bar(self.filesize/2, "Extracting homes")
        with open(self.file, "r") as entrada:
            for line in entrada:
                line = line.strip()
                self.extractHome(line)
                bar.progress()
        bar.finish()

        bar = Bar(self.filesize/2, "Extracting INCO, CODU, MAXCON and EDGEP")
        with open(self.file, "r") as entrada:
            for line in entrada:
                line = line.strip()
                bar.progress()
                self.extractMetrics(self.metrics, line)
        edges = self.topoGraph.edgeSet()
        bar.finish()

        if "TOPO" in self.metrics:
            bar = Bar(len(edges), "Extracting TOPO and SOCOR")
            for edge in edges:
                bar.progress()
                src = edge.src
                trg = edge.target
                enc = Encounter(int(src), int(trg))

                if (enc.toString() not in self.totalNeighbors):
                    self.totalNeighbors[enc.toString()] = []

                neighborsSrc = self.topoGraph.get_vertex(src).get_connections()
                degreeSrc = len(neighborsSrc)
                neighborsTrg = self.topoGraph.get_vertex(trg).get_connections()
                degreeDest = len(neighborsTrg)

                exists = 0
                if (self.topoGraph.containsEdge(src, trg)):
                    exists = 1

                to = 0
                for t in neighborsTrg:
                    if t in neighborsSrc:
                        to += 1
                numerator = float(to)+1
                denominator = ((degreeSrc - exists) + (degreeDest - exists) - to) + 1
                if denominator == 0:
                    denominator = 1
                toPct = numerator / denominator
                self.topo[enc.toString()] = toPct
            bar.finish()

        if "EDGEP" in self.metrics:
            self.normalizeEDGEP()
        if "SOCOR" in self.metrics:
            self.extractSOCOR()

        self.printMetrics(self.metrics)

    def normalizeEDGEP(self):
        keys = self.edgep.keys()
        for key in keys:
            denominator = (math.floor((self.maxTime / 86400)))
            if denominator == 0:
                denominator = 1
            self.edgep[key] = self.edgep[key] / denominator

    def printMAXCON(self):
        with open(self.metricFiles["MAXCON"], 'w') as saida:
            autocorrelations = self.autoCorrelation(self.maxcon, 24)
            for ac in autocorrelations:
                saida.write("{}\n".format(ac))

    def printTRVD(self):
        with open(self.metricFiles["TRVD"], 'w') as saida:
            for key, item in self.trvd.items():
                totalDist = sum([t.distance for t in item])
                totalDist = totalDist/len(item) if len(item) > 0 else 0.0
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key, totalDist))
                else:
                    saida.write("{}\n".format(totalDist))

    def printRADG(self):
        with open(self.metricFiles["RADG"], 'w') as saida:
            for key, item in self.radius.items():
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key, item))
                else:
                    saida.write("{}\n".format(item))

    def printCONEN(self):
        with open(self.metricFiles["CONEN"], 'w') as saida:
            for key, item in self.usersContacts.items():
                summ = sum([v for v in item.values()])
                summ = max(summ, 1)
                entropy = 0
                for v in item.values():
                    entropy += (v/summ) * math.log2((1/(v/summ)))
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key, entropy))
                else:
                    saida.write("{}\n".format(entropy))

    def printSPAV(self):
        with open(self.metricFiles["SPAV"], 'w') as saida:
            for key, item in self.usersVenues.items():
                summ = sum([v for v in item.values()])
                summ = max(summ, 1)
                entropy = 0
                for v in item.values():
                    entropy += (v/summ) * math.log2((1/(v/summ)))
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key, entropy))
                else:
                    saida.write("{}\n".format(entropy))

    def printVIST(self):
        with open(self.metricFiles["VIST"], 'w') as saida:
            for key, item in self.vist.items():
                vistd = sum([item for key, item in item.items()])
                vistd = vistd/max(len(item), 1)
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key, vistd))
                else:
                    saida.write("{}\n".format(vistd))

    def printEDGEP(self):
        with open(self.metricFiles["EDGEP"], 'w') as saida:
            for key, item in self.edgep.items():
                if self.REPORT_ID:
                    key = key.split(" ")
                    usr1, usr2 = key[0], key[1]
                    saida.write("{},{},{}\n".format(usr1, usr2, item))
                else:
                    saida.write("{}\n".format(item))

    
    def printGeneric(self, name, struct):
        with open(self.metricFiles[name], 'w') as saida:
            for key, item in struct.items():
                if self.REPORT_ID:
                    if " " in key:
                        key = key.split(" ")
                        usr1, usr2 = key[0], key[1]
                        strr = "{},{}".format(usr1, usr2)
                    else:
                        strr = "{}".format(key)
                    strr += ",{}\n".format(item)
                    saida.write(strr)

    def printTOPO(self):
        with open(self.metricFiles["TOPO"], 'w') as saida:
            for key, item in self.topo.items():
                if self.REPORT_ID:
                    key = key.split(" ")
                    usr1, usr2 = key[0], key[1]
                    saida.write("{},{},{}\n".format(usr1, usr2, item))
                else:
                    saida.write("{}\n".format(item))

    # TODO: delete file if it exits in the beginnning
    def extractINCO(self, line):
        with open(self.metricFiles["INCO"], 'a') as saida:

            components = line.strip().split(" ")
            user1 = components[0]
            user2 = components[1]
            incoEncounters = []
            if (self.incoGraph.containsEdge(user1, user2)):
                enc = Encounter(int(user1), int(user2))
                incoEncounters = self.inco[enc.toString()]
                w = float(self.incoGraph.getEdgeWeight(user1, user2))
                incoEncounters.append(float(components[2]) - float(w))
                self.inco[enc.toString()] = incoEncounters
                if self.REPORT_ID:
                    time = float(components[2]) - w
                    saida.write("{},{},{}\n".format(user1, user2, time))
                else:
                    saida.write("{}\n".format(float(components[2]) - w))
                self.incoGraph.add_edge(user1, user2, float(components[3]))
            else:
                self.incoGraph.add_vertex(user1)
                self.incoGraph.add_vertex(user2)
                encounter = Encounter(int(user1), int(user2))
                self.inco[encounter.toString()] = []
                self.incoGraph.add_edge(user1, user2, float(components[3]))

    def extractCODU(self, line):
        with open(self.metricFiles["CODU"], 'a') as saida:
            components = line.strip().split(" ")
            user1, user2 = components[0], components[1]
            timeI = float(components[3])
            timeF = float(components[2])
            if self.REPORT_ID:
                saida.write("{},{},{}\n".format(user1, user2, timeF - timeI))
            else:
                saida.write("{}\n".format(timeF - timeI))

    def extractMAXCON(self, line):
        components = line.strip().split(" ")
        hour = int((float(components[3]) / 3600))
        self.maxcon[hour] += 1

    def extractEDGEP(self, line):

        components = line.strip().split(" ")
        encounterDay = int(math.floor(float(components[3]) / 86400))
        encounter = Encounter(int(components[0]), int(components[1]))
        enc = encounter.toString()

        if (enc not in self.edgep):
            self.edgep[enc] = 1.0
            self.encounters[enc] = encounterDay
        else:
            if (self.encounters[enc] != encounterDay):
                self.edgep[enc] = self.edgep[enc] + 1
                self.encounters[enc] = encounterDay

    def extractTOPO(self, line):
        components = line.strip().split(" ")
        user1 = components[0]
        user2 = components[1]

        self.topoGraph.add_vertex(user1)
        self.topoGraph.add_vertex(user2)

        if (not self.topoGraph.containsEdge(user1, user2)):
            self.topoGraph.add_edge(user1, user2)

    def extractSOCOR(self):
        with open(self.metricFiles["SOCOR"], "w+") as saida:
            self.socor = 0
            stdDeviationTOPO = self.calculateStandardDeviation(self.topo)
            stdDeviationEDGEP = self.calculateStandardDeviation(self.edgep)
            covariance = self.calculateCovariance()
            divisor = (stdDeviationEDGEP * stdDeviationTOPO)
            self.socor = covariance/divisor if divisor != 0 else 0
            if(self.socor != 0):
                saida.write("{}\n".format(self.socor))
            else:
                saida.write("There is no correlation.\n")


    def trim(self, fileName):
        i = len(fileName) - 1
        while (fileName[i] != '\\' and i >= 0):
            i -= 1
        return fileName[i + 1:]

    def calculateCovariance(self):
        covariance = 0
        meanTOPO = self.calculateMean(self.topo)
        meanEDGEP = self.calculateMean(self.edgep)
        keys = self.topo.keys()
        if len(keys) > 0:
            for key in keys:
                topo = self.topo[key]
                edgep = self.edgep[key]
                if (topo is not None and edgep is not None):
                    covariance += (topo - meanTOPO) * (edgep - meanEDGEP)
            covariance /= len(keys)
        return covariance

    def calculateStandardDeviation(self, values):
        standardDeviation = 0
        mean = self.calculateMean(values)

        keys = values.keys()

        if len(keys) - 1 > 0:
            for key in keys:
                standardDeviation += (values[key] - mean) ** 2
            standardDeviation /= (len(keys) - 1)

        return math.sqrt(standardDeviation)

    def calculateMean(self, values):
        valid_values = [i for k, i in values.items() if i is not None]
        mean = sum(valid_values) / max(len(valid_values), 1)
        return mean

    def extractLocations(self):
        bar = Bar(self.filesize/2, "Extracting locations")
        with open(self.file, 'r') as entrada:
            for line in entrada:
                split = line.strip().split(" ")
                key = "{} {}".format(split[5], split[6])
                if key not in self.locations:
                    self.locations[key] = self.locationsIndex
                    self.locationsIndex += 1

                key = "{} {}".format(split[7], split[8])
                if key not in self.locations:
                    self.locations[key] = self.locationsIndex
                    self.locationsIndex += 1
                bar.progress()
        bar.finish()

    def extractVenues(self):
        numberVenues = int(self.maxX * self.maxY / (self.r * self.r))
        numberVenues = min(835, numberVenues)

        _set = list(self.locations.keys())
        randomIndex = 0
        venuesIndex = 0
        bar = Bar(numberVenues, "Extracting venues")
        for i in range(0, numberVenues):
            randomIndex = random.randint(0, len(_set) - 1)
            while _set[randomIndex] not in self.locations:
                randomIndex = random.randint(0, len(_set) - 1)
            self.venues[venuesIndex] = _set[randomIndex]
            venuesIndex += 1
            bar.progress()
        bar.finish()


    """
        getClosestVenue params x (String): x coordinate of users location y
        (String): y coordinate of users location return venue (String): closest
        venue to users location
    """
    def getClosestVenue(self, x, y):
        _set = list(self.venues.keys())
        minimum_distance = sys.float_info.max
        closest_venue = 0

        for i in range(0, len(_set)):
            venueLoc = self.venues[_set[i]].split(" ")
            distance = self.euclideanDistance(x, y, venueLoc[0], venueLoc[1])
            if (distance < minimum_distance):
                minimum_distance = distance
                closest_venue = _set[i]
        return self.venues[closest_venue]

    """
        extractHome - Obtains the home location for each user in the trace params
        line (String): line to be parsed return
    """
    def extractHome(self, line):
        components = line.strip().split(" ")
        firstUserLocation = self.getClosestVenue(components[5], components[6])
        firstUser = components[0]

        if (firstUser in self.userHomes):
            if (self.userHomes[firstUser].location == firstUserLocation):
                userHome = self.userHomes[firstUser]
                userHome.degree += 1
                self.userHomes[firstUser] = userHome
            elif (self.userHomes[firstUser].degree == 0):
                userHome = self.userHomes[firstUser]
                userHome.location = firstUserLocation
                userHome.degree += 1
                self.userHomes[firstUser] = userHome
            else:
                userHome = self.userHomes[firstUser]
                userHome.degree -= 1
                self.userHomes[firstUser] = userHome
        else:
            self.userHomes[firstUser] = Home(firstUserLocation, 1)

        secondUserLocation = self.getClosestVenue(components[7], components[8])
        secondUser = components[1]

        if (secondUser in self.userHomes):
            if (self.userHomes[secondUser].location == secondUserLocation):
                userHome = self.userHomes[secondUser]
                userHome.degree += 1
                self.userHomes[secondUser] = userHome
            else:
                if (self.userHomes[secondUser].degree == 0):
                    userHome = self.userHomes[secondUser]
                    userHome.location = secondUserLocation
                    userHome.degree += 1
                    self.userHomes[secondUser] = userHome
                else:
                    userHome = self.userHomes[secondUser]
                    userHome.degree -= 1
                    self.userHomes[secondUser] = userHome
        else:
            self.userHomes[secondUser] = Home(secondUserLocation, 1)

    """
        extractRADG params line (String): line to be processed return
    """
    def extractRADG(self, line):
        components = line.strip().split(" ")
        user1, user2 = components[0], components[1]
        user1Home = self.userHomes[user1].location
        user2Home = self.userHomes[user2].location
        user1Distance = self.euclideanDistance(components[5], components[6],
                                               user1Home.split(" ")[0],
                                               user1Home.split(" ")[1])

        user2Distance = self.euclideanDistance(components[7], components[8],
                                               user2Home.split(" ")[0],
                                               user2Home.split(" ")[1])

        if user1 in self.radius:
            self.radius[user1] = max(self.radius[user1], user1Distance)
        else:
            self.radius[user1] = user1Distance

        if user2 in self.radius:
            self.radius[user2] = max(self.radius[user2], user2Distance)
        else:
            self.radius[user2] = user2Distance

    def extractTRVD(self, line):
        comps = line.strip().split(" ")
        user1, user2 = comps[0], comps[1]

        if (user1 in self.trvd):
            lastPosition = self.trvd[user1][-1].location
            distance = self.euclideanDistance(comps[5], comps[6],
                                              lastPosition.split(" ")[0],
                                              lastPosition.split(" ")[1])
            userList = self.trvd[user1]
            userList.append(TravelPair(comps[5] + " " + comps[6], distance))
            self.trvd[user1] = userList
        else:
            userList = []
            userList.append(TravelPair(comps[5] + " " + comps[6], 0.0))
            self.trvd[user1] = userList

        if (user2 in self.trvd):
            lastPosition = self.trvd[user2][-1].location
            distance = self.euclideanDistance(comps[7], comps[8],
                                              lastPosition.split(" ")[0],
                                              lastPosition.split(" ")[1])
            userList = self.trvd[user2]
            userList.append(TravelPair(comps[7] + " " + comps[8], distance))
            self.trvd[user2] = userList
        else:
            userList = []
            userList.append(TravelPair(comps[7] + " " + comps[8], 0.0))
            self.trvd[user2] = userList

    def voronoi(self):
        if "SPAV" not in self.metrics and "VIST" not in self.metrics and "CONEN" not in self.metrics:
            return

        with open(self.file, 'r') as entrada:
            bar = Bar(self.filesize/2, "Extracting SPAV, CONEN and VIST")
            for line in entrada:

                split = line.strip().split(" ")

                user1 = split[0]
                user1X, user1Y = float(split[5]), float(split[6])

                user2 = split[1]
                user2X, user2Y = float(split[7]), float(split[8])

                time = float(split[4])

                if "CONEN" in self.metrics:
                    if user1 in self.usersContacts:
                        current_value = self.usersContacts[user1].get(user2, 0)
                        self.usersContacts[user1][user2] = current_value + 1
                    else:
                        self.usersContacts[user1] = {}
                    if user2 in self.usersContacts:
                        current_value = self.usersContacts[user2].get(user1, 0)
                        self.usersContacts[user2][user1] = current_value + 1
                    else:
                        self.usersContacts[user2] = {}

                distanceToCloser1 = distanceToCloser2 = sys.float_info.max
                user1Venue = user2Venue = 0

                if "SPAV" in self.metrics or "VIST" in self.metrics:
                    for i in range(0, len(self.venues)):

                        splitVe = [float(c) for c in self.venues[i].split(" ")]
                        dist = self.euclideanDistance(user1X, user1Y,
                                                      splitVe[0],
                                                      splitVe[1])
                        if (dist < distanceToCloser1):
                            distanceToCloser1 = dist
                            user1Venue = i

                        dist = self.euclideanDistance(user2X, user2Y,
                                                      splitVe[0],
                                                      splitVe[1])
                        if (dist < distanceToCloser2):
                            distanceToCloser2 = dist
                            user2Venue = i

                if "SPAV" in self.metrics:
                    if user1 in self.usersVenues:
                        currValue = self.usersVenues[user1].get(user1Venue, 0)
                        self.usersVenues[user1][user1Venue] = currValue + 1
                    else:
                        self.usersVenues[user1] = {}

                    if user2 in self.usersVenues:
                        currValue = self.usersVenues[user2].get(user2Venue, 0)
                        self.usersVenues[user2][user2Venue] = currValue + 1
                    else:
                        self.usersVenues[user2] = {}


                if "VIST" in self.metrics:
                    # Extracts Visit Time for user 1
                    if (user1 in self.vist):
                        visitTime = self.vist[user1].get(user1Venue, 0.0)
                        self.vist[user1][user1Venue] = visitTime + time
                    else:
                        self.vist[user1] = {}

                    # Extracts Visit Time for user 2
                    if (user2 in self.vist):
                        visitTime = self.vist[user2].get(user2Venue, 0.0)
                        self.vist[user2][user1Venue] = visitTime + time
                    else:
                        self.vist[user2] = {}

                bar.progress()
        bar.finish()

    def euclideanDistance(self, x1, y1, x2, y2):
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

    def autoCorrelation(self, values, lag):
        autocorrelations = float(lag)
        for i in range(0, lag):
            summ = 0
            for j in range(0, lag-1):
                summ += values[j] * values[j + i]

            autocorrelations[i] = summ
        return autocorrelations

