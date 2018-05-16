from Graph import Graph
from Graph import Vertex
from Graph import Edge
from Encounter import Encounter
import sys
import math
import random
import os
from Bar import Bar

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
    def __init__(self, filename, maxTime, maxX, maxY, r, filesize):
 
        self.file = filename
        self.maxTime = maxTime
        self.maxX = maxX
        self.maxY = maxY
        self.r = r
        self.filesize = filesize
        self.initialize(self.file)

    def initialize(self, filename):
        if not os.path.exists("filesForFitting.txt"):
            open("filesForFitting.txt", "w")
        self.filesForFitting = open("filesForFitting.txt", 'r+')
        self.inco = {} #<String, LinkedList<Double>>
        self.incoWriter = open(self.generateFileName(filename, "inco"), 'w')
        self.incoGraph = Graph()
        self.codu = {} #<String, LinkedList<Double>>
        self.coduWriter = open(self.generateFileName(filename, "codu"), 'w')
        self.maxcon = [0] * (int(self.maxTime/3600) + 1)
        self.edgep = {} #<String, Double>
        self.encounters = {} #<String, Integer>
        self.topo = {} #<String, Double>
        self.totalNeighbors = {} #<String, LinkedList<String>>
        self.topoGraph = Graph()
        self.socorWriter = open(self.generateFileName(filename, "socor"), 'w')
        self.locations = {} #<String, Integer>
        self.locationsIndex = 0
        self.venues = {} #<Integer, String>
        self.usersVenues = {} #<Integer, Integer>
        self.userHomes = {} #<String, Home>
 
        self.radius = {} #<String, Double>
        self.trvd = {} #<String, LinkedList<TravelPair>>
        self.vist = {} #<String, HashMap<Integer, Double>>


    def extractMetrics(self,metrics,line):
        functions = {"INCO": self.extractINCO, "CODU": self.extractCODU, "MAXCON": self.extractMAXCON, "EDGEP": self.extractEDGEP,
                     "TOPO": self.extractTOPO, "Home": self.extractHome, "TRVD": self.extractTRVD, "RADG": self.extractRADG}
        for m in metrics:
            functions[m](line)
 
    def extract(self):
 
        #try:
        self.voronoi()
       # self.extractVenues()
        i = 0

        bar = Bar(self.filesize,"Extracting INCO, CODU, MAXCON and EDGEP")
        with open(self.file, "r") as entrada:
            for line in entrada:
                self.inn = inn
                
                bar.progress()

                self.extractMetrics(["INCO", "CODU", "MAXCON", "EDGEP", "TOPO", "Home", "TRVD", "RADG"],line)

        edges = self.topoGraph.edgeSet()
        bar.finish()
        i = 0
        bar = Bar(self.filesize,"Extracting TOPO and SOCOR")
        for edge in edges:
            bar.progress()
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
        bar.finish()
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
       # self.printMAXCON() TODO check error on autocorrelation
        self.printEDGEP()
        self.printTOPO()
        self.printTabela()

        self.printRADG()
        self.printTRVD()
        self.printVIST()


        self.incoWriter.close()
        self.coduWriter.close()
        self.socorWriter.close()
        self.filesForFitting.close()

    #def printMetric(self,name,values,sumByKey = False):
    #    with open(self.generateFileName(self.file,name), 'w') as saida:
    #        for key,item in values.items():
    #            if sumByKey:
    #                total = sum()
    #            saida.write("{}, {}\n".format(key,item))
    def generateFileName(self, filename, characteristic):
        if "." in filename:
            filename = filename.replace(".","_" + characteristic + ".")
        else:
            filename += "_{}".format(characteristic)

        self.filesForFitting.write(str(self.trim(filename)) + "\n")
        return filename
 
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
        with open(self.generateFileName(self.file,"maxcon"), 'w') as saida:
            autocorrelations = self.autoCorrelation(self.maxcon, 24)
            for ac in autocorrelations:
                saida.write("{}\n".format(ac))
 
    def printTRVD(self):
        with open(self.generateFileName(self.file,"trvd"), 'w') as saida: 
            for key,item in self.trvd.items():
                totalDistance = sum([t.distance for t in item])
                totalDistance = totalDistance/len(item) if len(item) > 0 else 0.0
                saida.write("{},{}\n".format(key,totalDistance))

    def printRADG(self):
        with open(self.generateFileName(self.file,"radg"), 'w') as saida:
            for key,item in self.radius.items():
                saida.write("{},{}\n".format(key,item))

    def printVIST(self):
        with open(self.generateFileName(self.file,"vist"), 'w') as saida:
            for key,item in self.vist.items():
                vistd = sum([item for key,item in item.items()])
                vistd = 0 if len(item) == 0 else vistd/len(items)
                saida.write("{},{}\n".format(key,vistd))

    def printEDGEP(self):
        with open(self.generateFileName(self.file,"edgep"), 'w') as saida:
            for key,item in self.edgep.items():
                saida.write("{},{}\n".format(key,item))
    
    def printTOPO(self):
        with open(self.generateFileName(self.file,"topo"), 'w') as saida:
            for key,item in self.topo.items():
                saida.write("{},{}\n".format(key,item))
 
 
    def extractINCO(self, line):
        with open(self.generateFileName(self.file,"inco"), 'a+') as saida:
            
            components = line.strip().split(" ")
            user1 = components[0]
            user2 = components[1]
     
            incoEncounters = []
     
            if (self.incoGraph.containsEdge(user1, user2)):
                encounter = Encounter(int(user1), int(user2))
                incoEncounters = self.inco[encounter.toString()]
                w = float(self.incoGraph.getEdgeWeight(user1,user2))
                incoEncounters.append(float(components[2]) - float(w))
                self.inco[encounter.toString()] =  incoEncounters
                self.incoWriter.write("{}\n".format(float(components[2]) - w))
                self.incoGraph.add_edge(user1, user2, float(components[3]))
     
            else:
                self.incoGraph.add_vertex(user1)
                self.incoGraph.add_vertex(user2)
                encounter = Encounter(int(user1), int(user2))
                self.inco[encounter.toString()] = []
                self.incoGraph.add_edge(user1, user2, float(components[3]))
 
    def extractCODU(self, line):
        with open(self.generateFileName(self.file,"codu"), 'a+') as saida:
            components = line.strip().split(" ")
            timeI = float(components[3])
            timeF = float(components[2])
            saida.write("{}\n".format(timeF - timeI))
 
    def extractMAXCON(self, line):
        components = line.strip().split(" ")
        hour = int((float(components[3]) / 3600))
        self.maxcon[hour] += 1
 
    def extractEDGEP(self, line):
 
        components = line.strip().split(" ")
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
        components = line.strip().split(" ")
        user1 = components[0]
        user2 = components[1]
 
        self.topoGraph.add_vertex(user1)
        self.topoGraph.add_vertex(user2)
 
        if (not self.topoGraph.containsEdge(user1, user2)):
            self.topoGraph.add_edge(user1, user2)

    def extractSOCOR(self):
        self.socor = 0
        standardDeviationTOPO = self.calculateStandardDeviation(self.topo)
        standardDeviationEDGEP = self.calculateStandardDeviation(self.edgep)
        covariance = self.calculateCovariance()
        # print("\nSTDTOPO = " + standardDeviationTOPO)
        # print("\nSTDEDGEP = " + standardDeviationEDGEP)
        # print("\nCOV = " + covariance)
        divisor = (standardDeviationEDGEP * standardDeviationTOPO)
        self.socor = covariance/divisor if divisor > 0 else 0
        socorI = self.socor
        if (socorI != None):
            self.socorWriter.write("" + str(self.socor))
        else:
            self.socorWriter.write("Impossible to calculate socor, there is no correlation.")
 
 
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
                if (self.topo[key] != None and self.edgep[key] != None):
                    covariance += (self.topo[key] - meanTOPO) * (self.edgep[key] - meanEDGEP)
            covariance /= len(keys)
        return covariance
 
    def calculateStandardDeviation(self, map):
        standardDeviation = 0
        mean = self.calculateMean(map)
 
        keys = map.keys()
        
        if len(keys) - 1 > 0:
            for key in keys:    
                if (map[key] != None):
                    standardDeviation += (map[key] - mean) ** 2
            standardDeviation /= (len(keys) - 1)
 
        return math.sqrt(standardDeviation)
 
    def calculateMean(self,values):
        valid_values = [item for key,item in values.items() if item != None]
        mean = sum(valid_values) / max(len(valid_values),1)
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
        split = line.strip().split(" ")
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
 
    '''
    extractRADG params line (String): line to be processed return
      
    '''
    def extractRADG(self, line):
        components = line.strip().split(" ")
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
        components = line.strip().split(" ")
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
                split = line.strip().split(" ") # Changed this from \t to space
     
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