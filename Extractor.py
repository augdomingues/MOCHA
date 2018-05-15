from Graph import Graph
from Graph import Vertex
from Graph import Edge
from Encounter import Encounter
import sys
import math
import random

class Home:
    def __init__(self, l, d):
        self.location = l
        self.degree = d

class TravelPair:
    def __init__(self, string, distance2):
        self.distance = distance2
        self.location = string

class Location:
    def __init__(self, l, vt):
        self.location = l
        self.visitTime = vt

class Extractor:
    def __init__(self, file, maxTime, maxX, maxY, r, lines):
 
        self.file = file
        self.maxTime = maxTime
        self.maxX = maxX
        self.maxY = maxY
        self.r = r
        self.lines = lines
        self.initialize(self.file)
 
    def initialize(self, file):
        self.filesForFitting = open("filesForFitting.txt", 'r+')
        self.inco = {} #<String, LinkedList<Double>>
        self.incoWriter = open(self.generateFileName(file, "inco"), 'w')
        self.incoGraph = Graph()
        self.codu = {} #<String, LinkedList<Double>>
        self.coduWriter = open(self.generateFileName(file, "codu"), 'w')
        self.maxcon = [0] * (int(self.maxTime/3600) + 1)
        self.maxconWriter = open(self.generateFileName(file, "maxcon"), 'w')
        self.edgep = {} #<String, Double>
        self.encounters = {} #<String, Integer>
        self.edgepWriter = open(self.generateFileName(file, "edgep"), 'w')
        self.topo = {} #<String, Double>
        self.totalNeighbors = {} #<String, LinkedList<String>>
        self.topoGraph = Graph()
        self.topoWriter = open(self.generateFileName(file, "topo"), 'w')
        self.socorWriter = open(self.generateFileName(file, "socor"), 'w')
        self.locations = {} #<String, Integer>
        self.locationsIndex = 0
        self.venues = {} #<Integer, String>
        self.usersVenues = {} #<Integer, Integer>
        self.userHomes = {} #<String, Home>
 
        self.radius = {} #<String, Double>
        self.radgWriter = open(self.generateFileName(file, "radg"), 'w')
        self.trvd = {} #<String, LinkedList<TravelPair>>
        self.trvdWriter = open(self.generateFileName(file, "trvd"), 'w')
        self.vist = {} #<String, HashMap<Integer, Double>>
        self.vistWriter = open(self.generateFileName(file, "vist"), 'w')
 
    def extract(self):
 
        #try:
            self.voronoi()
            self.extractVenues()
            i = 0
            self.progressPercentage(100, 100)
            print("\nExtracting INCO, CODU, MAXCON and EDGEP")
            with open(self.file) as inn:
                _lines = inn. readlines()
                for line in _lines:
                    self.inn = inn
                    self.progressPercentage(i, self.lines)
                    i += 1
                    self.extractINCO(line)
                    self.extractCODU(line)
                    self.extractMAXCON(line)
                    self.extractEDGEP(line)
                    self.extractTOPO(line)
                    self.extractHome(line)
                    self.extractTRVD(line)
                    self.extractRADG(line)


            edges = self.topoGraph.edgeSet()
 
            i = 0
            self.progressPercentage(100, 100)
            print("\nExtracting TOPO and SOCOR")
            for edge in edges:
                self.progressPercentage(i, len(edges))
                i += 1
                source = edge.src
                target = edge.target
                encounter = Encounter(int(source), int(target))
 
                if (encounter.toString() not in self.totalNeighbors):
                    self.totalNeighbors[encounter.toString()] = []
 
                # LinkedList<String> neighborsSource = new
                # LinkedList<String>(Graphs.neighborListOf(topoGraph, source));
 
                # LinkedList<String> neighborsTarget = new
                # LinkedList<String>(Graphs.neighborListOf(topoGraph, target));
 
                neighborsSource = self.topoGraph.get_vertex(source).get_connections()
                degreeSrc = len(neighborsSource)
                neighborsTarget = self.topoGraph.get_vertex(target).get_connections()
                degreeDest = len(neighborsTarget)
 
                edgeExists = 0
                if (self.topoGraph.containsEdge(source, target)):
                    edgeExists = 1
 
                edgesTO = neighborsSource

                for aux in neighborsTarget:
                    edgesTO.remove(aux)
 
                to = len(edgesTO)
 
                toPct = (float(to) / ((degreeSrc - edgeExists) + (degreeDest - edgeExists) - to))
 
                topo[encounter.toString()] = toPct
 
                # HashSet<String> a = new HashSet<>(neighborsTarget);
                # for (String string : neighborsSource) {
                # for (String string2 : neighborsTarget) {
                # if
                # (!totalNeighbors.get(encounter.toString()).contains(string))
                # {
                # LinkedList<String> newList =
                # totalNeighbors.get(encounter.toString());
                # newList.add(string);
                # totalNeighbors.put(encounter.toString(), newList);
                # }
                #
                # if
                # (!totalNeighbors.get(encounter.toString()).contains(string2))
                # {
                # LinkedList<String> newList =
                # totalNeighbors.get(encounter.toString());
                # newList.add(string2);
                # totalNeighbors.put(encounter.toString(), newList);
                # }
                #
                # if (string.equals(string2)) {
                #
                # if (topo.containsKey(encounter.toString())) {
                # topo.put(encounter.toString(), topo.get(encounter.toString())
                # + 1);
                # } else {
                # topo.put(encounter.toString(), 1.0)
            
            self.normalizeEDGEP()
            self.extractSOCOR()
            self.printMAXCON()
            self.printEDGEP()
            self.printTOPO()
            self.printTabela()
 
            self.printRADG()
            self.printTRVD()
            self.printVIST()
 
            self.radgWriter.close()
            self.vistWriter.close()
            self.trvdWriter.close()
 
            self.incoWriter.close()
            self.coduWriter.close()
            self.maxconWriter.close()
            self.edgepWriter.close()
            self.topoWriter.close()
            self.socorWriter.close()
            self.filesForFitting.close()
        #except Exception, e:
        #    print "Extract"
        #    print(e)
 
    def printTabela(self):
        out = open('table.csv','w')
        keys = self.topo.keys()
        for key in keys:
            out.write(str(key) + ";" + str(self.topo[key]) + ";" + str(self.edgep[key]) + "\n")
        out.close()
 
    def normalizeEDGEP(self):
        keys = self.edgep.keys()
        for key in keys:
            self.edgep[key] =  self.edgep[key] / (math.floor((self.maxTime / 86400)))
 
    def printMAXCON(self):
 
        autocorrelations = self.autoCorrelation(self.maxcon, 24)

        for i in range (0, len(autocorrelations)):
            self.maxconWriter.write(str(autocorrelations[i]) + "\n")
 
    def printTRVD(self):
        keys = self.trvd.keys()
        for key in keys:
            totalDistance = 0
            _list = self.trvd[key]
            for t in _list:
                totalDistance += t.distance
                self.trvdWriter.write(str(t.distance) + "\n")
            # self.trvdWriter.write(totalDistance/list.size() + "\n")

    def printRADG(self):
        keys = self.radius.keys()
        for key in keys:
            self.radgWriter.write(str(self.radius[key]) + "\n")

    def printVIST(self):
        keys = self.vist.keys()
        for key in keys:
            vistd = 0
            visits = self.vist[key]
            visit_keys = visits.keys()
            for v in visit_keys:
                vistd += visits[v]
                self.vistWriter.write(str(visits[v]) + "\n")
            # if(vistd == 0):
            #   self.vistWriter.write("0.0\n")
            # else:
            #   self.vistWriter.write(vistd/len(visit_keys) + "\n")
 
    def printEDGEP(self):
        keys = self.edgep.keys()
        for key in keys:
            self.edgepWriter.write(str(self.edgep[key]) + "\n")
 
    def extractINCO(self, line):
 
        components = line.split(" ")
        user1 = components[0]
        user2 = components[1]
 
        incoEncounters = []
 
        if (self.incoGraph.containsEdge(user1, user2)):
            encounter = Encounter(int(user1), int(user2))
            incoEncounters = self.inco[encounter.toString()]
            incoEncounters.append(float(components[2]) - float(self.incoGraph.getEdgeWeight(user1, user2)))
            self.inco[encounter.toString()] =  incoEncounters
            self.incoWriter.write(str(float(components[2]) - float(self.incoGraph.getEdgeWeight(user1, user2))) + "\n")
            self.incoGraph.add_edge(user1, user2, float(components[3]))
 
        else:
            self.incoGraph.add_vertex(user1)
            self.incoGraph.add_vertex(user2)
            encounter = Encounter(int(user1), int(user2))
            self.inco[encounter.toString()] = []
            self.incoGraph.add_edge(user1, user2, float(components[3]))
 
    def extractCODU(self, line):
        components = line.split(" ")
        timeI = float(components[3])
        timeF = float(components[2])
 
        self.coduWriter.write(str(timeF - timeI) + "\n")
 
    def extractMAXCON(self, line):
        components = line.split(" ")
        hour = int((float(components[3]) / 3600))
        self.maxcon[hour] += 1
 
    def extractEDGEP(self, line):
 
        components = line.split(" ")
        encounterDay = int(math.floor(float(components[3]) / 86400))
        encounter = Encounter(int(components[0]), int(components[1]))
 
        if (encounter.toString() not in self.edgep):
            # print("Nao existia aresta " + encounter.toString()
            # + ", criei uma, com edgep valendo 1 e o dia do encontro foi " +
            # encounterDay);
            self.edgep[encounter.toString()] = 1.0
            self.encounters[encounter.toString()] = encounterDay
        else:
            if (self.encounters[encounter.toString()] != encounterDay):
                # print("Ja existia uma aresta entre " +
                # encounter.toString() + " e o dia de encontro foi diferente,
                # antes era " + encounters.get(encounter.toString()) + " agora
                # e " + encounterDay);
                self.edgep[encounter.toString()] = self.edgep[encounter.toString()] + 1
                self.encounters[encounter.toString()] = encounterDay
 
        # if (edgep.containsKey(encounter.toString()) &&
        # encounters.get(encounter.toString()) != encounterDay) {
        # edgep.put(encounter.toString(), edgep.get(encounter.toString()) + 1);
        # encounters.put(encounter.toString(), encounterDay);
        # } else {
        # edgep.put(encounter.toString(), 1.0);
        # encounters.put(encounter.toString(), encounterDay);
        # }
 
    def extractTOPO(self, line):
        components = line.split(" ")
        user1 = components[0]
        user2 = components[1]
 
        self.topoGraph.add_vertex(user1)
        self.topoGraph.add_vertex(user2)
 
        if (not self.topoGraph.containsEdge(user1, user2)):
            self.topoGraph.add_edge(user1, user2)

    def printTOPO(self):
        keys = topo.keys()
        for key in keys:
            self.topoWriter.write(str(self.topo[key]) + "\n")
 
    def extractSOCOR(self):
        self.socor = 0
        standardDeviationTOPO = self.calculateStandardDeviation(topo)
        standardDeviationEDGEP = self.calculateStandardDeviation(edgep)
        covariance = self.calculateCovariance()
        # print("\nSTDTOPO = " + standardDeviationTOPO)
        # print("\nSTDEDGEP = " + standardDeviationEDGEP)
        # print("\nCOV = " + covariance)
        self.socor = covariance / (standardDeviationEDGEP * standardDeviationTOPO)
        socorI = socor
        if (self.socorI != None):
            self.socorWriter.write("" + str(self.socor))
        else:
            self.socorWriter.write("Impossible to calculate socor, there is no correlation.")
 
    def generateFileName(self, file, characteristic):
        fileName = file
        fileName = fileName.replace(".","_" + characteristic + ".")
        self.filesForFitting.write(str(self.trim(fileName)) + "\n")
        return fileName
 
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
        for key in keys:
            if (self.topo[key] != None and self.edgep[key] != None):
                covariance += (self.topo[key] - meanTOPO) * (self.edgep[key] - meanEDGEP)
        covariance /= len(keys)
        return covariance
 
    def calculateStandardDeviation(self, map):
        standardDeviation = 0
        mean = self.calculateMean(map)
 
        keys = map.keys()
 
        for key in keys:
            if (map[key] != None):
                standardDeviation += (map[key] - mean) ** 2
        standardDeviation /= (len(keys) - 1)
 
        return math.sqrt(standardDeviation)
 
    def calculateMean(self,map):
        keys = map.keys()
        mean = 0
        for key in keys:
            if (map[key] != None):
                mean += map[key]
        mean /= len(keys)
 
        return mean
 
    def progressPercentage(self, remain, total):
        if (remain > total):
            raise ValueError('IllegalArgumentException')
        maxBareSize = 10; # 10unit for 100%
        remainProcent = int(((100 * remain) / total) / maxBareSize)
        defaultChar = '-'
        bare = ""
        icon = "*"
        for i in range (0, maxBareSize):
            bare += defaultChar
        bare += "]"
        bareDone = "["
        for i in range (0, remainProcent):
            bareDone += icon

        bareRemain = bare[remainProcent: len(bare)]
        print(chr(27) + "[2J")
        print("\r" + bareDone + bareRemain + " " + str(remainProcent * 10) + "%")

        if remain == total:
            print("\n")
 
    def extractLocations(self, line):
        split = line.split(" ")
        try:
            aux = self.locations[split[5] + " " + split[6]]
        except:
            self.locations[split[5] + " " + split[6]] = self.locationsIndex
            self.locationsIndex += 1
 
        try:
            aux = self.locations[split[7] + " " + split[8]]
        except:
            self.locations[split[7] + " " + split[8]] = self.locationsIndex
            self.locationsIndex += 1
 
    def extractVenues(self):
        numberVenues = int(self.maxX * self.maxY / (self.r * self.r))
        numberVenues = 835


        _set = self.locations.keys()
        randomIndex = 0
        venuesIndex = 0
 
        for i in range (0,numberVenues):
            randomIndex = random.randint(0, len(_set))
            try:
                while (self.venues[self.locations[_set[randomIndex]]] != None):
                    randomIndex = random.randint(0, len(_set))
            except:
                pass
            if randomIndex == len(_set):
                randomIndex -= 1
            self.venues[venuesIndex] = _set[randomIndex]
            venuesIndex += 1
 
    def euclidianDistance(self, x1, y1, x2, y2):
        return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))
 
    '''
    getClosestVenue params x (String): x coordinate of users location y
    (String): y coordinate of users location return venue (String): closest
    venue to users location
    '''

    def getClosestVenue(self, x, y):
        _set = self.venues.keys()
        minimum_distance = sys.float_info.max
        closest_venue = 0
 
        for i in range (0, len(_set)):
            venue_location = self.venues[_set[i]].split(" ")
            distance = self.euclideanDistance(float(x), float(y), float(venue_location[0]), float(venue_location[1]))
            if (distance < minimum_distance):
                minimum_distance = distance
                closest_venue = _set[i]
 
        return self.venues[closest_venue]
 
    # Example of line in MOCHA parsed trace:
    # 223 330 1782802.315 1782802.229 0.08599999989382923 0.303 0.843 0.318
    # 0.821
    # Should be the closest to the venues??
 
    '''
    extractHome - Obtains the home location for each user in the trace params
    line (String): line to be parsed return
    '''
    
    def extractHome(self, line):
        components = line.split(" ")
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
 
    '''
    extractRADG params line (String): line to be processed return
      
    '''
    def extractRADG(self, line):
        components = line.split(" ")
        firstUser = components[0]
        secondUser = components[1]
 
        firstUserHome = self.userHomes[firstUser].location
        secondUserHome = self.userHomes[secondUser].location
 
        firstUserDistance = self.euclideanDistance(float(components[5]), float(components[6]), float(firstUserHome.split(" ")[0]), float(firstUserHome.split(" ")[1]))
        secondUserDistance = self.euclideanDistance(float(components[7]), float(components[8]), float(secondUserHome.split(" ")[0]), float(secondUserHome.split(" ")[1]))
 
        # Checks if lastly extracted radius is bigger than stored user radius
        if (firstUser in self.radius):
            if (self.radius[firstUser] < firstUserDistance):
                self.radius[firstUser] = firstUserDistance
        else:
            self.radius[firstUser] = firstUserDistance
 
        if (secondUser in self.radius):
            if (self.radius[secondUser] < secondUserDistance):
                self.radius[secondUser] = secondUserDistance
        else:
            self.radius[secondUser] = secondUserDistance
 
    def extractTRVD(self, line):
        components = line.split(" ")
        firstUser = components[0]
        secondUser = components[1]
 
        if (firstUser in self.trvd):
            lastPosition = self.trvd[firstUser][-1].location
            distance = self.euclideanDistance(float(components[5]), float(components[6]), float(lastPosition.split(" ")[0]), float(lastPosition.split(" ")[1]))
            userList = self.trvd[firstUser]
            userList.append(TravelPair(components[5] + " " + components[6], distance))
            self.trvd[firstUser] = userList
        else:
            userList = []
            userList.append(TravelPair(components[5] + " " + components[6], 0.0))
            self.trvd[firstUser] = userList
 
        if (secondUser in self.trvd):
            lastPosition = self.trvd[secondUser][-1].location
            distance = self.euclideanDistance(float(components[7]), float(components[8]), float(lastPosition.split(" ")[0]), float(lastPosition.split(" ")[1]))
            userList = self.trvd[secondUser]
            userList.append(TravelPair(components[7] + " " + components[8], distance))
            self.trvd[secondUser] = userList
        else:
            userList = []
            userList.append(TravelPair(components[7] + " " + components[8], 0.0))
            self.trvd[secondUser] = userList
 
    def voronoi(self):
        # TODO Verificar a geracao do nome
        # BufferedWriter out = new BufferedWriter(new FileWriter(new
        # File("saida.txt")));
        with open(self.file) as inn:
            _lines = inn. readlines()
            for line in _lines:
                self.extractLocations(line)
                split = line.split(" ") # Changed this from \t to space
     
                user1 = int(split[0])
                user1X = float(split[5])
                user1Y = float(split[6])
     
                user2 = int(split[1])
                user2X = float(split[7])
                user2Y = float(split[8])
     
                time = float(split[4])
     
                distanceToCloser1 = sys.float_info.max
                distanceToCloser2 = sys.float_info.max
                user1Venue = 0
                user2Venue = 0
     
                for i in range (0, len(self.venues)):
     
                    splitVenues = self.venues[i].split(" ")
                    distance = self.euclideanDistance(user1X, user1Y, float(splitVenues[0]), float(splitVenues[1]))
                    if (distance < distanceToCloser1):
                        distanceToCloser1 = distance
                        user1Venue = i
     
                    distance = self.euclideanDistance(user2X, user2Y, float(splitVenues[0]), float(splitVenues[1]))
                    if (distance < distanceToCloser2):
                        distanceToCloser2 = distance
                        user2Venue = i
     
                try:
                    if (self.usersVenues[user1] != user1Venue):
                        self.usersVenues[user1] = user1Venue
                except:
                    self.usersVenues[user1] = user1Venue
     
                try:
                    if (self.usersVenues[user2] != user2Venue):
                        self.usersVenues[user2] = user2Venue
                except:
                    self.usersVenues[user2] = user2Venue
     
                # Extracts Visit Time for user 1
                if (split[0] in self.vist):
                    if (user1Venue in self.vist[split[0]]):
                        visitTime = self.vist[split[0]][user1Venue]
                        self.vist[split[0]][user1Venue] = visitTime + time
                    else:
                        self.vist[split[0]][user1Venue] = 0.0
                else:
                    self.vist[split[0]] = {}
     
                # Extracts Visit Time for user 2
                if (split[1] in self.vist):
                    if (user2Venue in self.vist[split[1]]):
                        visitTime = self.vist[split[1]][user2Venue]
                        self.vist[split[1]][user2Venue] = visitTime + time
                    else:
                        self.vist[split[1]][user2Venue] = 0.0
                else:
                    self.vist[split[1]] = {}
 
    def euclideanDistance(self, x1, y1, x2, y2):
        return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

    def autoCorrelation(self, values, lag):
        autocorrelations = float(lag)
 
        for i in range (0, lag):
            sum = 0
            for j in range(0, lag-1):
                sum += values[j] * values[j + i]

            autocorrelations[i] = sum
        return autocorrelations