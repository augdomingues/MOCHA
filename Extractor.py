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
    def __init__(self, filename, maxTime, maxX, maxY, r, filesize, metrics):
        
        # Checks if system is windows to create folder correctly
        self.barra = "\\" if os.name == 'nt' else "/"
        self.folderName = filename.split(".")[0].replace("_parsed", "") + "_metrics_folder{}".format(self.barra)
        self.file, self.filesize = filename, filesize
        self.generatedFileNames = {}
        self.maxX, self.maxY, self.r, self.maxTime = maxX, maxY, r, maxTime
        self.metrics = [key for key in metrics.keys()]
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
        self.userHomes = {}
        self.radius = {}
        self.trvd = {}
        self.vist = {}

        if not os.path.exists(self.folderName):
            os.makedirs(self.folderName)
        with open("filesForFitting.txt", "w+") as fitting:
            for key in self.metrics:
                filename = "{}{}.txt".format(self.folderName,key)
                with open(filename, "w+") as saida:
                    pass
                fitting.write("{}\n".format(filename))
                self.metricFiles[key] = filename


    def printMetrics(self,metrics):
        functions = {"EDGEP": self.printEDGEP, "TOPO": self.printTOPO, "RADG": self.printRADG, "TRVD": self.printTRVD, "VIST": self.printVIST,
                     "MAXCON": self.printMAXCON}

        for m in metrics:
            if m in functions:
                functions[m]()

    def extractMetrics(self,metrics,line):
        functions = {"INCO": self.extractINCO, "CODU": self.extractCODU, "MAXCON": self.extractMAXCON, "EDGEP": self.extractEDGEP,
                     "TOPO": self.extractTOPO, "TRVD": self.extractTRVD, "RADG": self.extractRADG}
        for m in metrics:
            if m in functions:
                functions[m](line)
 
    def extract(self):
 
        self.voronoi()
        self.extractVenues()
        bar = Bar(self.filesize,"Extracting homes")
        with open(self.file, "r") as entrada:
            for line in entrada:
                line = line.strip()
                self.extractHome(line)
                bar.progress()
        bar.finish()

        bar = Bar(self.filesize,"Extracting INCO, CODU, MAXCON and EDGEP")
        with open(self.file, "r") as entrada:
            for line in entrada:
                line = line.strip()
                bar.progress()
                self.extractMetrics(self.metrics,line)#, "Home", "TRVD", "RADG"],line)
        edges = self.topoGraph.edgeSet()
        bar.finish()
        
        if "TOPO" in self.metrics:
            bar = Bar(len(edges),"Extracting TOPO and SOCOR")
            for edge in edges:
                bar.progress()
                source = edge.src
                target = edge.target
                encounter = Encounter(int(source), int(target))

                if (encounter.toString() not in self.totalNeighbors):
                    self.totalNeighbors[encounter.toString()] = []

                neighborsSource = self.topoGraph.get_vertex(source).get_connections()
                degreeSrc = len(neighborsSource)
                neighborsTarget = self.topoGraph.get_vertex(target).get_connections()
                degreeDest = len(neighborsTarget)

                edgeExists = 0
                if (self.topoGraph.containsEdge(source, target)):
                    edgeExists = 1

                to = 0
                for t in neighborsTarget:
                    if t in neighborsSource:
                        to += 1
                numerator = float(to)+1
                denominator = ((degreeSrc - edgeExists) + (degreeDest - edgeExists) - to)+1
                if denominator == 0:
                    denominator = 1
                toPct = numerator / denominator
                self.topo[encounter.toString()] = toPct
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
            self.edgep[key] =  self.edgep[key] / denominator
 
    def printMAXCON(self):
        with open(self.metricFiles["MAXCON"], 'w') as saida:
            autocorrelations = self.autoCorrelation(self.maxcon, 24)
            for ac in autocorrelations:
                saida.write("{}\n".format(ac))
 
    def printTRVD(self):
        with open(self.metricFiles["TRVD"], 'w') as saida:
            for key,item in self.trvd.items():
                totalDistance = sum([t.distance for t in item])
                totalDistance = totalDistance/len(item) if len(item) > 0 else 0.0
                saida.write("{}\n".format(totalDistance))

    def printRADG(self):
        with open(self.metricFiles["RADG"], 'w') as saida:
            for key,item in self.radius.items():
                saida.write("{}\n".format(item))

    def printVIST(self):
        with open(self.metricFiles["VIST"], 'w') as saida:
            for key,item in self.vist.items():
                vistd = sum([item for key,item in item.items()])
                vistd = vistd/max(len(item),1)#  0 if len(item) == 0 else vistd/len(items)
                saida.write("{}\n".format(vistd))

    def printEDGEP(self):
        with open(self.metricFiles["EDGEP"], 'w') as saida:
            for key,item in self.edgep.items():
                saida.write("{}\n".format(item))
    
    def printTOPO(self):
        with open(self.metricFiles["TOPO"],'w') as saida:
            for key,item in self.topo.items():
                saida.write("{}\n".format(item))
 
    # TODO: delete file if it exits in the beginnning
    def extractINCO(self, line):
        with open(self.metricFiles["INCO"], 'a') as saida:
            
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
                saida.write("{}\n".format(float(components[2]) - w))
                self.incoGraph.add_edge(user1, user2, float(components[3]))
     
            else:
                self.incoGraph.add_vertex(user1)
                self.incoGraph.add_vertex(user2)
                encounter = Encounter(int(user1), int(user2))
                self.inco[encounter.toString()] = []
                self.incoGraph.add_edge(user1, user2, float(components[3]))
 
    def extractCODU(self, line):
        with open(self.metricFiles["CODU"],'a') as saida:
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
        with open(self.metricFiles["SOCOR"], "w+") as saida:
            self.socor = 0
            standardDeviationTOPO = self.calculateStandardDeviation(self.topo)
            standardDeviationEDGEP = self.calculateStandardDeviation(self.edgep)
            covariance = self.calculateCovariance()
            divisor = (standardDeviationEDGEP * standardDeviationTOPO)
            self.socor = covariance/divisor if divisor > 0 else 0
            if(self.socor > 0):
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
                if (self.topo[key] != None and self.edgep[key] != None):
                    covariance += (self.topo[key] - meanTOPO) * (self.edgep[key] - meanEDGEP)
            covariance /= len(keys)
        return covariance
    
    #TODO: Replace by numpy calculation
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


        _set = list(self.locations.keys())
        randomIndex = 0
        venuesIndex = 0
        bar = Bar(numberVenues,"Extracting venues")
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
            bar.progress()
        bar.finish()
 
 
    '''
    getClosestVenue params x (String): x coordinate of users location y
    (String): y coordinate of users location return venue (String): closest
    venue to users location
    '''

    def getClosestVenue(self, x, y):
        _set = list(self.venues.keys())
        minimum_distance = sys.float_info.max
        closest_venue = 0
 
        for i in range (0, len(_set)):
            venue_location = self.venues[_set[i]].split(" ")
            distance = self.euclideanDistance(float(x), float(y), float(venue_location[0]), float(venue_location[1]))
            if (distance < minimum_distance):
                minimum_distance = distance
                closest_venue = _set[i]
        #print("***************************************Tamanho do venues: " + str(len(self.venues)) + "******************************************")
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
        ##print(self.userHomes)
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
                #print(split)
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
