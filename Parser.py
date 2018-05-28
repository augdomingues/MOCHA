import math
import os
from Encounter import Encounter
from PositionEntry import PositionEntry
from Cell import Cell
from Graph import Graph
from Graph import Vertex
from User import User
from Bar import Bar

class Parser:
 
    def __init__(self, r):
        self.r = r
        self.maxX = 0
        self.maxY = 0
        self.maxT = 0
        self.filesize = 0
        self.parsedfilesize = 0
 
    def parseSwim(self, filename):

        #print("*****filename: " + filename + "*****")


        self.collectMaxesSwim(filename)
        newFile = self.generateFileName(filename)
        #print("*****newfile: " + newFile + "*****")
        with open(newFile, 'w') as out:
            encounters = {}
            bar = Bar(self.filesize, "Parsing SWIM file")
            with open(filename, 'r') as entrada:
                for i,line in enumerate(entrada):
                    #self.progressPercentage(i, self.filesize)
                    bar.progress()

                    components = line.strip().split(" ")
                    components = self.removeEmpty(components)
                    
                    encounter = Encounter(components[2], components[3])
                    
                    if encounter.toString() in encounters:
                        e = encounters[encounter.toString()]
                        self.parsedfilesize+=1
                        out.write("{} {} {} {} {} {} {} {} {}\n".format(components[2],components[3],components[0],e,(float(components[0])-e),components[4],components[5],components[6],components[7]))
                    encounters[encounter.toString()] = float(components[0])
        bar.finish()
        return newFile
 
    def removeEmpty(self, components):
        return [c for c in components if c != ""]
 
    def preParseRaw(self, filename):
        with open(filename,'r') as entrada:
            print("Pre parsing...", end="")
            for line in entrada:

                self.filesize += 1
                components = line.split(" ")
                coordinateX = float(components[1])
                coordinateY = float(components[2])
                time = float(components[3])

                self.maxT = int(max(time,self.maxT))
                self.maxX = int(math.ceil(max(coordinateX,self.maxX)))
                self.maxY = int(math.ceil(max(coordinateY,self.maxY)))


    """
        collectMaxes: parse the entire trace looking for the highest values for X,Y and time
        params:
            filename: name of the trace
        returns:
            -
    """
    def collectMaxes(self, filename):
        with open(filename) as entrada:
            for line in entrada:
                self.filesize += 1
                self.filesize += 1
                
                components = line.strip().split(" ")
                
                time = float(components[3])
                
                coordinateXUser1 = float(components[5])
                coordinateYUser1 = float(components[6])
     
                coordinateXUser2 = float(components[7])
                coordinateYUser2 = float(components[8])
     

                self.maxX = math.ceil(max(coordinateXUser1, coordinateXUser2, self.maxX))
                self.maxY = math.ceil(max(coordinateYUser1, coordinateYUser2, self.maxY))
                self.maxT = max(time,self.maxT)
     
    def collectMaxesSwim(self, filename):
        with open(filename, 'r') as entrada:
            for line in entrada:

                self.filesize += 1
                components = line.split(" ")
                components = self.removeEmpty(components)
                
                time = float(components[0])
                
                coordinateXUser1 = float(components[4])
                coordinateYUser1 = float(components[5])
     
                coordinateXUser2 = float(components[6])
                coordinateYUser2 = float(components[7])

                self.maxX = math.ceil(max(coordinateXUser1, coordinateXUser2, self.maxX))
                self.maxY = math.ceil(max(coordinateYUser1, coordinateYUser2, self.maxY))
                self.maxT = max(time,self.maxT)
     
    def parseRaw(self, filename):
        self.preParseRaw(filename)
 
        cells = {} # HashMap<String, LinkedList<User>> 
 
        g = Graph()

        positionDictionary = {} # HashMap<String, PositionEntry>
 
        beginingPositions = {} # HashMap<String, String> 

        with open(self.generateFileName(filename),'w+') as out:
            newLines = 0
            bar = Bar(self.filesize, "Parsing RAW file")
            with open(filename) as entrada:
                for i,line in enumerate(entrada):
                    bar.progress()
                    components = line.split(" ")
                    
                    _id = int(components[0])
                    positionX = float(components[1])
                    positionY = float(components[2])
                    coordX = math.floor(positionX / self.r)
                    coordY = math.floor(positionY / self.r)
                    time = float(components[3])
                    
                    user = User(_id, positionX, positionY)
         
                    try:
                        entry = positionDictionary[user.toString()]
         
                        if (entry.positionX != positionX or entry.positionY != positionY):
         
                            # The node moved
                            oldCell = Cell(entry.coordX, entry.coordY)
         
                            usersInCell = cells[oldCell.toString()]
                            usersInCell = self.removeUserFromCell(usersInCell, user.toString())
                            cells[oldCell.toString()] = usersInCell
                             
                            oldUser = User(_id, entry.positionX, entry.positionY)
                             
                            adjacent = self.getAdjacentCellUsers(cells, oldUser, self.r)
         
                            newCell = Cell(coordX, coordY)
                            try:
                                usersInCell = cells[newCell.toString()]
                                usersInCell.append(user)
                                cells[newCell.toString()] = usersInCell
                            except:
                                usersInCell = []
                                usersInCell.append(user)
                                cells[newCell.toString()] = usersInCell
                             
                            for user2 in adjacent:
                                if euclidean(user.x, user.y, user2.x, user2.y) <= self.r:
                                    vert1 = g.get_vertex(user.toString())
                                    conected = False

                                    for vert2 in vert1.get_connections():
                                        if vert2.get_id() == user2.toString():
                                            conected = True
                                            g.add_edge(user.toString(), user2.toString(), time)
                                            break
                                    
                                    if not conected:
                                        g.add_edge(user.toString(), user2.toString(), time)
                                        encounter = Encounter(int(user.toString()), int(user2.toString()))
                                        beginingPositions[encounter.toString()] = str(user.x) + " " + str(user.y) + " " + str(user2.x) + " " + str(user2.y)
                                elif (g.containsEdge(user.toString(), user2.toString())):
                                    encounter = Encounter(int(user.toString()), int(user2.toString()))
                                    beginingPosistion = beginingPositions[encounter.toString()]
                                    out.write(generateEntry(user, user2, time, g, beginingPosistion))
                                    newLines += 1
                                    g.removeEdge(user.toString(), user2.toString())

                            newEntry = PositionEntry(positionX, positionY, coordX, coordY, time)
                            positionDictionary[user.toString()] = newEntry

                    except:
                        newEntry = PositionEntry(positionX, positionY, coordX, coordY, time)
                        positionDictionary[user.toString()] = newEntry

                        g.add_vertex(user.toString())
         
                        newCell = Cell(coordX, coordY)
                        try:
                            usersInCell = cells[newCell.toString()]
                            usersInCell.append(user)
                            cells[newCell.toString()] = usersInCell
                        except:
                            usersInCell = []
                            usersInCell.append(user)
                            cells[newCell.toString()] = usersInCell

                    rangeXBegin = 0
                    if (coordX - 1 > 0):
                        rangeXBegin = coordX - 1
          
                    rangeYBegin = 0
                    if (coordY - 1 > 0):
                        rangeYBegin = coordY - 1

                    while (rangeXBegin <= coordX + 1):
                        while (rangeYBegin <= coordY + 1):
                            newCell = Cell(rangeXBegin, rangeYBegin)
                            try:
                                usersInCell = cells[newCell.toString()]
                                for user2 in usersInCell:
                                    if (user.toString() != user2.toString()):
                                        if euclidean(user.x, user.y, user2.x, user2.y) <= self.r:
                                            if (g.containsEdge(user.toString(), user2.toString())):
                                                g.add_edge(user.toString(), user2.toString(), time)
                                            else:
                                                g.add_edge(user.toString(), user2.toString(), time)
                                                encounter = Encounter(int(user.toString()), int(user2.toString()))
                                                beginingPositions[encounter.toString()] = str(user.x) + " " + str(user.y) + " " + str(user2.x) + " " + str(user2.y)
                                        elif (g.containsEdge(user.toString(), user2.toString())):
                                            encounter = Encounter(int(user.toString()), int(user2.toString()))
                                            beginingPosistion = beginingPositions[encounter.toString()]
                                            out.write(generateEntry(user, user2, time, g, beginingPosistion))
                                            newLines += 1
                                            g.removeEdge(user.toString(), user2.toString())
                            except:
                                pass
                            rangeYBegin += 1

                        if (coordX - 1 > 0):
                            rangeYBegin = coordY - 1
                        else:
                            rangeYBegin = 0
                        rangeXBegin += 1

        self.filesize = newLines
        bar.finish()
        #return self.generateFileName(filename)
 
    def removeUserFromCell(self, usersInCell, id):

        toBeRemoved = User(0, 0, 0)
        for user in usersInCell:
            if (user.toString() == id):
                toBeRemoved = user
        usersInCell.remove(toBeRemoved)
        return usersInCell
 
    def generateFileName(self, filename):
        filename = os.path.abspath(filename)
        if "." in filename:
            name,extension = filename.split(".")[0], filename.split(".")[1]
            filename = "{}_parsed.{}".format(name,extension)
        else:
            filename = "{}_parsed".format(filename)
        
        if os.path.exists(filename):
            ow = input("\nFile already exists. Are you sure you want to overwrite? (y/n): ")
            if ow not in ["True","true", "TRUE", "Y", "y", "1", "yes", "YES", "Yes"]:
                raise SystemExit(0)
        
        
        
        return filename
 
    def generateEntry(self, user, user2, time, g, beginingPosition):
        w = g.getEdgeWeight(user.toString(),user2.toString())
        entry = "{} {} {} {} {} {}\n".format(user.id,user2.id,time,w,(time - w), beginingPosition)
        return entry
 
    def getAdjacentCellUsers(self, cells, user, r):
        adjacent = []
 
        k = math.floor(user.x / r)
        rangeXBegin = k - 1 if k - 1 > 0 else 0
 
        l = math.floor(user.x / r)
        rangeYBegin = l - 1 if l - 1 > 0 else 0
 
        while rangeXBegin <= k + 1:
            while rangeYBegin <= l + 1:
                newCell = Cell(rangeXBegin, rangeYBegin)
                if newCell.toString() in cells:
                    usersInCell = cells[newCell.toString()]
                    for user2 in usersInCell:
                        if (user.toString() != user2.toString()):
                            if euclidean(user.x, user.y, user2.x, user2.y) <= r:
                                adjacent.append(user2)
                rangeYBegin += 1
            rangeXBegin += 1
        return adjacent
 
    def euclidean(self, xi, yi, xj, yj):
        return math.sqrt(((xi - xj) ** 2) + ((yi - yj) ** 2))
 
    def progressPercentage(self, remain, total):
        if (remain > total):
            raise ValueError('IllegalArgumentException')
        maxBareSize = 10 # 10unit for 100%
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
        print("\r" + bareDone + bareRemain + " " + str(remainProcent * 10) + "%", end="")

        if remain == total:
            print("\n")

 
    def parseNS2(self, file):
        self.collectMaxesNS2(file)
        out = open(self.generateFileName(file),'w')

        i = 0
        print("Parsing file!\n")
        with open(file) as inn:
            _lines = inn. readlines()
            for line in _lines:
                self.progressPercentage(i, self.filesize)
                i += 1
                components = line.split(" ")
             
        out.close()
        return self.generateFileName(file)
 
    def collectMaxesNS2(self, file):
        pass
        # TODO Auto-generated method stub
