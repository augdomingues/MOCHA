import math
import os
from Encounter import Encounter
from PositionEntry import PositionEntry
from Cell import Cell
from Graph import Graph
from Graph import Vertex
from User import User
from Bar import Bar
import pdb


class Parser:

    def __init__(self, r):
        self.r = r
        self.maxX = 0
        self.maxY = 0
        self.maxT = 0
        self.filesize = 0
        self.parsedfilesize = 0

    def parseSwim(self, filename):
        self.collectMaxesSwim(filename)
        newFile = self.generateFileName(filename)
        with open(newFile, 'w') as out:
            encounters = {}
            bar = Bar(self.filesize, "Parsing SWIM file")
            with open(filename, 'r') as entrada:
                for i, line in enumerate(entrada):
                    bar.progress()
                    comps = line.strip().split(" ")
                    comps = self.removeEmpty(comps)
                    encounter = Encounter(comps[2], comps[3])
                    if encounter.toString() in encounters:
                        e = encounters[encounter.toString()]
                        self.parsedfilesize += 1
                        out.write("{} {} ".format(comps[2], comps[3]))
                        out.write("{} {} ".format(comps[3], e))
                        out.write("{} ".format(float(comps[0]) - e))
                        out.write("{} {} ".format(comps[4], comps[5]))
                        out.write("{} ".format(comps[6]))
                        out.write("{}\n".format(comps[7]))
                    encounters[encounter.toString()] = float(comps[0])
        bar.finish()
        return newFile

    def removeEmpty(self, components):
        return [c for c in components if c != ""]

    def preParseRaw(self, filename):
        with open(filename, 'r') as entrada:
            print("Pre parsing...", end="")
            for line in entrada:

                self.filesize += 1
                components = line.split(" ")
                coordinateX = float(components[1])
                coordinateY = float(components[2])
                time = float(components[3])

                self.maxT = int(max(time, self.maxT))
                self.maxX = int(math.ceil(max(coordinateX, self.maxX)))
                self.maxY = int(math.ceil(max(coordinateY, self.maxY)))

    """
        collectMaxes: look for the highest values for X,Y and time
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

                self.maxX = math.ceil(max(coordinateXUser1, self.maxX))
                self.maxX = math.ceil(max(coordinateXUser2, self.maxX))
                self.maxY = math.ceil(max(coordinateYUser1, self.maxY))
                self.maxY = math.ceil(max(coordinateYUser2, self.maxY))
                self.maxT = max(time, self.maxT)

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

                self.maxX = math.ceil(max(coordinateXUser1, self.maxX))
                self.maxX = math.ceil(max(coordinateXUser2, self.maxX))
                self.maxY = math.ceil(max(coordinateYUser1, self.maxY))
                self.maxY = math.ceil(max(coordinateYUser2, self.maxY))
                self.maxT = max(time, self.maxT)

    def parseRaw(self, filename):
        self.preParseRaw(filename)
        cells = {}
        g = Graph()
        positionDictionary = {}
        beginingPositions = {}
        with open(self.generateFileName(filename), 'w+') as out:
            newLines = 0
            bar = Bar(self.filesize, "Parsing RAW file")
            with open(filename) as entrada:
                for i, line in enumerate(entrada):
                    bar.progress()
                    components = line.split(" ")
                    _id = int(components[0])
                    posX = float(components[1])
                    posY = float(components[2])
                    coordX = math.floor(posX / self.r)
                    coordY = math.floor(posY / self.r)
                    time = float(components[3])

                    user = User(_id, posX, posY)
                    u1 = user.toString()
                    u1x, u1y = user.x, user.y

                    try:
                        entry = positionDictionary[u1]
                        entryX, entryY = entry.positionX, entry.positionY
                        if entryX != posX or entryY != posY:
                            # The node moved
                            oldCell = Cell(entry.coordX, entry.coordY)
                            usrInCell = cells[oldCell.toString()]
                            usrInCell = self.removeUserFromCell(usrInCell, u1)
                            cells[oldCell.toString()] = usrInCell
                            oldUser = User(_id, entryX, entryY)
                            r = self.r
                            adj = self.getAdjacentCellUsers(cells, oldUser, r)
                            newCell = Cell(coordX, coordY)
                            try:
                                usrInCell = cells[newCell.toString()]
                                usrInCell.append(user)
                                cells[newCell.toString()] = usrInCell
                            except:
                                usrInCell = []
                                usrInCell.append(user)
                                cells[newCell.toString()] = usrInCell

                            for user2 in adjacent:
                                u2x, u2y = user2.x, user2.y
                                u2 = user2.toString()
                                euc = self.euclidean(u1x, u1y, u2x, u2y)
                                if euc <= self.r:
                                    vert1 = g.get_vertex(u1)
                                    conected = False

                                    for vert2 in vert1.get_connections():
                                        if vert2.get_id() == u2:
                                            conected = True
                                            g.add_edge(u1, u2, time)
                                            g.add_edge(u2, u1, time)
                                            break

                                    if not conected:
                                        g.add_edge(u1, u2, time)
                                        g.add_edge(u2, u1, time)
                                        encounter = Encounter(int(u1), int(u2))
                                        enc = encounter.toString()
                                        pos = str(u1x) + " " + str(u1y) + " "
                                        pos += str(u2x) + " " + str(u2y)
                                        beginingPositions[enc] = pos

                                elif (g.containsEdge(u1, u2)):
                                    encounter = Encounter(int(u1), int(u2))
                                    enc = encounter.toString()
                                    beginPos = beginingPositions[enc]
                                    out.write(self.generateEntry(user, user2,
                                                                 time, g,
                                                                 beginPos))
                                    newLines += 1
                                    g.remove_edge(u1, u2)
                                    g.remove_edge(u2, u1)

                            e = PositionEntry(posX, posY, coordX, coordY, time)
                            positionDictionary[u1] = e

                    except:
                        e = PositionEntry(posX, posY, coordX, coordY, time)
                        positionDictionary[u1] = e

                        g.add_vertex(u1)

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
                                u1 = user.toString()
                                u1x, u1y = user.x, user.y
                                usersInCell = cells[newCell.toString()]
                                for user2 in usersInCell:
                                    u2 = user2.toString()
                                    u2x, u2y = user2.x, user2.y
                                    if (u1 != u2):
                                        eu = self.euclidean(u1x, u1y, u2x, u2y)
                                        if eu <= self.r:
                                            if (g.containsEdge(u1, u2)):
                                                g.add_edge(u1, u2, time)
                                                g.add_edge(u2, u1, time)
                                            else:
                                                g.add_edge(u1, u2, time)
                                                g.add_edge(u2, u1, time)
                                                e = Encounter(int(u1), int(u2))
                                                enc = e.toString()
                                                pos = str(u1x) + " " + str(u1y)
                                                pos += " " + str(u2x) + " "
                                                pos += str(u2y)
                                                beginingPositions[enc] = pos
                                        elif (g.containsEdge(u1, u2)):
                                            e = Encounter(int(u1), int(u2))
                                            enc = e.toString()
                                            beginPos = beginingPositions[enc]
                                            out.write(self.generateEntry(user,
                                                      user2, time,
                                                      g, beginPos))
                                            newLines += 1
                                            g.remove_edge(u1, u2)
                                            g.remove_edge(u2, u1)
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
        return self.generateFileName(filename)

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
            name, extension = filename.split(".")[0], filename.split(".")[1]
            filename = "{}_parsed.{}".format(name, extension)
        else:
            filename = "{}_parsed".format(filename)

        if os.path.exists(filename):
            ow = input("\nFile already exists. Overwrite it? (y/n): ")
            ow = ow.upper()
            if ow not in ["TRUE", "Y", "YES"]:
                raise SystemExit(0)

        return filename

    def generateEntry(self, user, user2, time, g, beginingPosition):
        w = g.getEdgeWeight(user.toString(), user2.toString())
        entry = "{} {} ".format(user.id, user2.id)
        entry += "{} {} {} ".format(time, w, (time - w))
        entry += "{}\n".format(beginingPosition)
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
                    for u2 in usersInCell:
                        if (user.toString() != u2.toString()):
                            if self.euclidean(user.x, user.y, u2.x, u2.y) <= r:
                                adjacent.append(u2)
                rangeYBegin += 1
            rangeXBegin += 1
        return adjacent

    def euclidean(self, xi, yi, xj, yj):
        return math.sqrt(((xi - xj) ** 2) + ((yi - yj) ** 2))

    def parseNS2(self, filename):
        self.collectMaxesNS2(filename)
        out = open(self.generateFileName(filename), 'w')

        i = 0
        print("Parsing file!\n")
        with open(filename) as entrada:
            for line in entrada:
                i += 1
                components = line.split(" ")

        out.close()
        return self.generateFileName(filename)

    def collectMaxesNS2(self, filename):
        pass
        # TODO Auto-generated method stub
