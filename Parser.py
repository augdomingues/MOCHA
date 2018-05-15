import math
import os
from Encounter import Encounter
from PositionEntry import PositionEntry
from Cell import Cell
from Graph import Graph
from Graph import Vertex
from User import User

class Parser:
 
    def __init__(self, r):
        self.r = r
        self.maxX = 0
        self.maxY = 0
        self.maxT = 0
        self.lines = 0
 
    def parseSwim(self, file):
        self.collectMaxesSwim(file)
        out = open(self.generateFileName(file),'w')

        encounters = {}
        i = 0
        print("Parsing file!\n")
        with open(file) as inn:
            _lines = inn. readlines()
            for line in _lines:
                self.progressPercentage(i, self.lines)
                i += 1
                components = line.split(" ")
                components = self.removeEmpty(components)
                encounter = Encounter(components[2], components[3])
                try:
                    aux = encounters[encounter.toString()]
                    out.write(components[2] + " " + str(components[3])) + " " + str(components[0]) + " " + str(encounters[encounter.toString()]) + " " + str(float(components[0]) - str(encounters[encounter.toString()]) + " " + str(components[4]) + " " + str(components[5]) + " " + str(components[6]) + " " + str(components[7]) + "\n")
                    encounters[encounter.toString()] = float(components[0])
                except:
                    encounters[encounter.toString()] = float(components[0])
        out.close()
        return file
 
    def removeEmpty(self, components):
        correctLine = []
        for i in range (0, len(components)):
            if (components[i] != ("")):
                correctLine.append(components[i])
        return correctLine
 
    def preParseRaw(self, file):
        with open(file) as inn:
            _lines = inn. readlines()
            for line in _lines:
                if (self.lines % 3 == 0):
                    print(chr(27) + "[2J")
                    print("\rPre parsing.")
                elif (self.lines % 3 == 1):
                    print(chr(27) + "[2J")
                    print("\rPre parsing..")
                else:
                    print(chr(27) + "[2J")
                    print("\rPre parsing...")

                self.lines += 1
                components = line.split(" ")
                coordinateX = float(components[1])
                coordinateY = float(components[2])
                time = float(components[3])
                if (coordinateX > self.maxX):
                    self.maxX = int(math.ceil(coordinateX))
     
                if (coordinateY > self.maxY):
                    self.maxY = int(math.ceil(coordinateY))
                     
                if (time > self.maxT):
                    self.maxT = int(time)
 
    def collectMaxes(self, file):
        try:
            with open(file) as inn:
                _lines = inn. readlines()
                for line in _lines:
                    self.lines += 1
                    components = line.split(" ")
                    coordinateXUser1 = float(components[5])
                    coordinateYUser1 = float(components[6])
         
                    coordinateXUser2 = float(components[7])
                    coordinateYUser2 = float(components[8])
         
                    time = float(components[3])
                    if (coordinateXUser1 > self.maxX):
                        self.maxX = math.ceil(coordinateXUser1)
         
                    if (coordinateXUser2 > self.maxX):
                        self.maxX = math.ceil(coordinateXUser2)
         
                    if (coordinateYUser1 > self.maxY):
                        self.maxY = math.ceil(coordinateYUser1)

                    if (coordinateYUser2 > self.maxY):
                        self.maxY = math.ceil(coordinateYUser2)
         
                    if (time > self.maxT):
                        self.maxT = time
        except:
            self.lines += 1
            components = line.split(" ")
            coordinateXUser1 = float(components[5])
            coordinateYUser1 = float(components[6])
     
            coordinateXUser2 = float(components[7])
            coordinateYUser2 = float(components[8])
     
            time = float(components[2])
            if (coordinateXUser1 > self.maxX):
                self.maxX = math.ceil(coordinateXUser1)
     
            if (coordinateXUser2 > self.maxX):
                self.maxX = math.ceil(coordinateXUser2)
     
            if (coordinateYUser1 > self.maxY):
                self.maxY = math.ceil(coordinateYUser1)
     
            if (coordinateYUser2 > self.maxY):
                self.maxY = math.ceil(coordinateYUser2)
     
            if (time > self.maxT):
                self.maxT = time

     
    def collectMaxesSwim(self, file):
        with open(file) as inn:
            _lines = inn. readlines()
            for line in _lines:
                self.lines += 1
                components = line.split(" ")
                components = self.removeEmpty(components)
                coordinateXUser1 = float(components[4])
                coordinateYUser1 = float(components[5])
     
                coordinateXUser2 = float(components[6])
                coordinateYUser2 = float(components[7])
     
                time = float(components[0])
                if (coordinateXUser1 > self.maxX):
                    self.maxX = math.ceil(coordinateXUser1)

                if (coordinateXUser2 > self.maxX):
                    self.maxX = math.ceil(coordinateXUser2)

                if (coordinateYUser1 > self.maxY):
                    self.maxY = math.ceil(coordinateYUser1)
     
                if (coordinateYUser2 > self.maxY):
                    self.maxY = math.ceil(coordinateYUser2)
     
                if (time > self.maxT):
                    self.maxT = time

    def parseRaw(self, file):
        self.preParseRaw(file)
 
        cells = {} # HashMap<String, LinkedList<User>> 
 
        g = Graph()

        positionDictionary = {} # HashMap<String, PositionEntry>
 
        beginingPositions = {} # HashMap<String, String> 

        out = open(self.generateFileName(file),'w')
        i = 0
        newLines = 0
        print("Parsing file!")
        with open(file) as inn:
            _lines = inn. readlines()
            for line in _lines:
                self.progressPercentage(i, self.lines)
                i += 1
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
                            if (euclidian(self.r, user.x, user.y, user2.x, user2.y)):
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
                                    if (euclidian(self.r, user.x, user.y, user2.x, user2.y)):
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

        out.close()
        self.lines = newLines
        return self.generateFileName(file)
 
    def removeUserFromCell(self, usersInCell, id):
        toBeRemoved = User(0, 0, 0)
        for user in usersInCell:
            if (user.toString() == id):
                toBeRemoved = user
        usersInCell.remove(toBeRemoved)
        return usersInCell
 
    def generateFileName(self, file):
        fileName = os.path.abspath(file)
        index = 0
        for i in range (len(fileName)-1, -1, -1):
            if (fileName[i] == '.'):
                index = i
                i = -1
        extention = fileName[index:]
        fileName = fileName[0: index]
        fileName += "_parsed"
        fileName += extention
        return fileName
 
    def generateEntry(self, user, user2, time, g, beginingPosition):
 
        return str(user.id) + " " + str(user2.id) + " " + str(time) + " " + g.getEdgeWeight(user.toString(), user2.toString()) + " " + (time - g.getEdgeWeight(user.toString(), user2.toString())) + " " + beginingPosition + "\n"
 
    def getAdjacentCellUsers(self, cells, user, r):
        adjacent = []
 
        rangeXBegin = 0
        k = math.floor(user.x / r)
        if (k - 1 > 0):
            rangeXBegin = k - 1
 
        rangeYBegin = 0
        l = math.floor(user.x / r)
        if (l - 1 > 0):
            rangeYBegin = l - 1
 
        while (rangeXBegin <= k + 1):
            while (rangeYBegin <= l + 1):
                newCell = Cell(rangeXBegin, rangeYBegin)
                try:
                    usersInCell = cells[newCell.toString()]
                    for user2 in usersInCell:
                        if (user.toString() != user2.toString()):
                            if (euclidian(r, user.x, user.y, user2.x, user2.y)):
                                adjacent.append(user2)
                except:
                    pass
                rangeYBegin += 1
            rangeXBegin += 1
        return adjacent
 
    def euclidian(self, r, xi, yi, xj, yj):
        distancia = math.sqrt(((xi - xj) ** 2) + ((yi - yj) ** 2))
        if (distancia <= r):
            return true
        return false

 
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
        print(chr(27) + "[2J")
        print("\r" + bareDone + bareRemain + " " + str(remainProcent * 10) + "%")

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
                self.progressPercentage(i, self.lines)
                i += 1
                components = line.split(" ")
             
        out.close()
        return self.generateFileName(file)
 
    def collectMaxesNS2(self, file):
        pass
        # TODO Auto-generated method stub