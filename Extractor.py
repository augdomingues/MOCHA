from Graph import Graph
from Graph import Vertex
from Graph import Edge
from Encounter import Encounter
import sys
import math
import random
import os
from Bar import Bar
import pdb

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

    def __init__(self, filename, maxTime, maxX, maxY, r, filesize, metrics, report_id):

        # Checks if system is windows to create folder correctly
        self.barra = "\\" if os.name == 'nt' else "/"
        #print("*****FILENAME: " + filename + "******")
        if "." in filename:
            self.folderName = filename.replace("_parsed.csv", "") + "_metrics_folder{}".format(self.barra)
        else:
            self.folderName = filename.replace("_parsed", "") + "_metrics_folder{}".format(self.barra)
        #print("O nome do arquivo eh " + filename)
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
        #pdb.set_trace()
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
                "MAXCON": self.printMAXCON, "SPAV": self.printSPAV, "CONEN": self.printCONEN}

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
        self.extractLocations()
        self.extractVenues()
        self.voronoi()
        bar = Bar(self.filesize/2,"Extracting homes")
        with open(self.file, "r") as entrada:
            for line in entrada:
                line = line.strip()
                self.extractHome(line)
                bar.progress()
        bar.finish()

        bar = Bar(self.filesize/2,"Extracting INCO, CODU, MAXCON and EDGEP")
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
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key,totalDistance))
                else:
                    saida.write("{}\n".format(totalDistance))

    def printRADG(self):
        with open(self.metricFiles["RADG"], 'w') as saida:
            for key,item in self.radius.items():
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key,item))
                else:
                    saida.write("{}\n".format(item))

    def printCONEN(self):
        with open(self.metricFiles["CONEN"],'w') as saida:
            for key,item in self.usersContacts.items():
                summ = sum([v for v in item.values()])
                summ = max(summ,1)
                entropy = 0
                entropy = sum([(v/summ) * math.log2((1/(v/summ))) for v in item.values()])
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key,entropy))
                else:
                    saida.write("{}\n".format(entropy))

    def printSPAV(self):
        with open(self.metricFiles["SPAV"], 'w') as saida:
            for key,item in self.usersVenues.items():
                summ = sum([v for v in item.values()])
                summ = max(summ,1)
                entropy = 0
                entropy = sum([(v/summ) * math.log2((1/(v/summ))) for v in item.values()])
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key,entropy))
                else:
                    saida.write("{}\n".format(entropy))


    def printVIST(self):
        with open(self.metricFiles["VIST"], 'w') as saida:
            for key,item in self.vist.items():
                vistd = sum([item for key,item in item.items()])
                vistd = vistd/max(len(item),1)#  0 if len(item) == 0 else vistd/len(items)
                if self.REPORT_ID:
                    saida.write("{},{}\n".format(key,vistd))
                else:
                    saida.write("{}\n".format(vistd))

    def printEDGEP(self):
        with open(self.metricFiles["EDGEP"], 'w') as saida:
            for key,item in self.edgep.items():
                if self.REPORT_ID:
                    saida.write("{},{},{}\n".format(key.split(" ")[0],key.split(" ")[1],item))
                else:
                    saida.write("{}\n".format(item))
    
    def printTOPO(self):
        with open(self.metricFiles["TOPO"],'w') as saida:
            for key,item in self.topo.items():
                if self.REPORT_ID:
                    saida.write("{},{},{}\n".format(key.split(" ")[0],key.split(" ")[1],item))
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
                encounter = Encounter(int(user1), int(user2))
                incoEncounters = self.inco[encounter.toString()]
                w = float(self.incoGraph.getEdgeWeight(user1,user2))
                incoEncounters.append(float(components[2]) - float(w))
                self.inco[encounter.toString()] =  incoEncounters
                if self.REPORT_ID:
                    saida.write("{},{},{}\n".format(user1,user2,float(components[2]) - w))
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
        with open(self.metricFiles["CODU"],'a') as saida:
            components = line.strip().split(" ")
            user1,user2 = components[0],components[1]
            timeI = float(components[3])
            timeF = float(components[2])
            if self.REPORT_ID:
                saida.write("{},{},{}\n".format(user1,user2,timeF - timeI))
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
 
        if (encounter.toString() not in self.edgep):
            self.edgep[encounter.toString()] = 1.0
            self.encounters[encounter.toString()] = encounterDay
        else:
            if (self.encounters[encounter.toString()] != encounterDay):
                self.edgep[encounter.toString()] = self.edgep[encounter.toString()] + 1
                self.encounters[encounter.toString()] = encounterDay

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
    def calculateStandardDeviation(self, values):
        standardDeviation = 0
        mean = self.calculateMean(values)

        keys = values.keys()

        if len(keys) - 1 > 0:
            for key in keys:    
                if (values[key] != None):
                    standardDeviation += (values[key] - mean) ** 2
            standardDeviation /= (len(keys) - 1)

        return math.sqrt(standardDeviation)

    def calculateMean(self,values):
        valid_values = [item for key,item in values.items() if item != None]
        mean = sum(valid_values) / max(len(valid_values),1)
        return mean

    def extractLocations(self):
        bar = Bar(self.filesize/2,"Extracting locations")
        with open(self.file, 'r') as entrada:
            for line in entrada:
                split = line.strip().split(" ")
                key = "{} {}".format(split[5],split[6])
                if key not in self.locations:
                    self.locations[key] = self.locationsIndex
                    self.locationsIndex += 1

                key = "{} {}".format(split[7],split[8])
                if key not in self.locations:
                    self.locations[key] = self.locationsIndex
                    self.locationsIndex += 1
                bar.progress()
        bar.finish()

    def extractVenues(self):
        numberVenues = int(self.maxX * self.maxY / (self.r * self.r))
        numberVenues = min(835,numberVenues)


        _set = list(self.locations.keys())
        randomIndex = 0
        venuesIndex = 0
        bar = Bar(numberVenues,"Extracting venues")
        for i in range (0,numberVenues):
            randomIndex = random.randint(0, len(_set) - 1)
            while _set[randomIndex] not in self.locations:
                randomIndex = random.randint(0,len(_set) - 1)
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
            distance = self.euclideanDistance(x,y,venue_location[0], venue_location[1])
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
        firstUser, secondUser = components[0], components[1]
        
        firstUserHome = self.userHomes[firstUser].location
        secondUserHome = self.userHomes[secondUser].location
 
        firstUserDistance = self.euclideanDistance(components[5], components[6], firstUserHome.split(" ")[0], firstUserHome.split(" ")[1])
        secondUserDistance = self.euclideanDistance(components[7], components[8], secondUserHome.split(" ")[0], secondUserHome.split(" ")[1])
 
        # Checks if lastly extracted radius is bigger than stored user radius (if none is stored, then lastly is added as bigger)
        self.radius[firstUser] = max(self.radius[firstUser],firstUserDistance) if firstUser in self.radius else firstUserDistance
        self.radius[secondUser] = max(self.radius[secondUser],firstUserDistance) if secondUser in self.radius else secondUserDistance
 
    def extractTRVD(self, line):
        components = line.strip().split(" ")
        firstUser, secondUser = components[0], components[1]
 
        if (firstUser in self.trvd):
            lastPosition = self.trvd[firstUser][-1].location
            distance = self.euclideanDistance(components[5], components[6], lastPosition.split(" ")[0], lastPosition.split(" ")[1])
            userList = self.trvd[firstUser]
            userList.append(TravelPair(components[5] + " " + components[6], distance))
            self.trvd[firstUser] = userList
        else:
            userList = []
            userList.append(TravelPair(components[5] + " " + components[6], 0.0))
            self.trvd[firstUser] = userList
 
        if (secondUser in self.trvd):
            lastPosition = self.trvd[secondUser][-1].location
            distance = self.euclideanDistance(components[7], components[8], lastPosition.split(" ")[0], lastPosition.split(" ")[1])
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
        if "SPAV" not in self.metrics and "VIST" not in self.metrics and "CONEN" not in self.metrics:
            return
        with open(self.file, 'r') as entrada:
            bar = Bar(self.filesize/2,"Extracting SPAV, CONEN and VIST")
            for line in entrada: 
        #        self.extractLocations(line)
                split = line.strip().split(" ") # Changed this from \t to space

                user1, user1X, user1Y = split[0], float(split[5]), float(split[6])

                user2, user2X, user2Y = split[1], float(split[7]), float(split[8])

                time = float(split[4])
                
                if "CONEN" in self.metrics:
                    if user1 in self.usersContacts:
                        current_value = self.usersContacts[user1].get(user2,0)
                        self.usersContacts[user1][user2] = current_value + 1
                    else:
                        self.usersContacts[user1] = {}
                    if user2 in self.usersContacts:
                        current_value = self.usersContacts[user2].get(user1,0)
                        self.usersContacts[user2][user1] = current_value + 1
                    else:
                        self.usersContacts[user2] = {}

                distanceToCloser1 = distanceToCloser2 = sys.float_info.max
                user1Venue = user2Venue =  0

                if "SPAV" in self.metrics or "VIST" in self.metrics:
                    for i in range (0, len(self.venues)):

                        splitVenues = [float(c) for c in self.venues[i].split(" ")]
                        distance = self.euclideanDistance(user1X, user1Y, splitVenues[0], splitVenues[1])
                        if (distance < distanceToCloser1):
                            distanceToCloser1 = distance
                            user1Venue = i

                        distance = self.euclideanDistance(user2X, user2Y, splitVenues[0], splitVenues[1])
                        if (distance < distanceToCloser2):
                            distanceToCloser2 = distance
                            user2Venue = i

                if "SPAV" in self.metrics:
                    if user1 in self.usersVenues:
                        current_value = self.usersVenues[user1].get(user1Venue,0)
                        self.usersVenues[user1][user1Venue] = current_value + 1
                    else:
                        self.usersVenues[user1] = {}

                    if user2 in self.usersVenues:
                        current_value = self.usersVenues[user2].get(user2Venue,0)
                        self.usersVenues[user2][user2Venue] = current_value + 1
                    else:
                        self.usersVenues[user2] = {}


                if "VIST" in self.metrics:
                    # Extracts Visit Time for user 1
                    # TODO Verificar com Fabricio se o else tem ' + time ' ou nao
                    if (user1 in self.vist):
                        visitTime = self.vist[user1].get(user1Venue,0.0)
                        self.vist[user1][user1Venue] = visitTime + time
                    else:
                        self.vist[user1] = {}

                    # Extracts Visit Time for user 2
                    # TODO Verificar com Fabricio se o else tem ' + time ' ou nao
                    if (user2 in self.vist):
                        visitTime = self.vist[user2].get(user2Venue,0.0)
                        self.vist[user2][user1Venue] = visitTime + time
                    else:
                        self.vist[user2] = {}

                bar.progress()
        bar.finish()

    def euclideanDistance(self, x1, y1, x2, y2):
        x1,y1,x2,y2 = float(x1),float(y1),float(x2),float(y2)
        return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))

    def autoCorrelation(self, values, lag):
        autocorrelations = float(lag)
        for i in range (0, lag):
            summ = 0
            for j in range(0, lag-1):
                summ += values[j] * values[j + i]

            autocorrelations[i] = summ
        return autocorrelations
