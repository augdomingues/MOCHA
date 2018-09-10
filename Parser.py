from math import floor, ceil, sqrt
import os
from Mocha_utils import (
        Encounter,
        PositionEntry,
        Cell,
        User
        )
from Graph import Graph
from Graph import Vertex
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
                    if str(encounter) in encounters:
                        e = encounters[str(encounter)]
                        self.parsedfilesize += 1
                        out.write("{} {} ".format(comps[2], comps[3]))
                        out.write("{} {} ".format(comps[3], e))
                        out.write("{} ".format(float(comps[0]) - e))
                        out.write("{} {} ".format(comps[4], comps[5]))
                        out.write("{} ".format(comps[6]))
                        out.write("{}\n".format(comps[7]))
                    encounters[str(encounter)] = float(comps[0])
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
                self.maxX = int(ceil(max(coordinateX, self.maxX)))
                self.maxY = int(ceil(max(coordinateY, self.maxY)))

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

                self.maxX = ceil(max(coordinateXUser1, self.maxX))
                self.maxX = ceil(max(coordinateXUser2, self.maxX))
                self.maxY = ceil(max(coordinateYUser1, self.maxY))
                self.maxY = ceil(max(coordinateYUser2, self.maxY))
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

                self.maxX = ceil(max(coordinateXUser1, self.maxX))
                self.maxX = ceil(max(coordinateXUser2, self.maxX))
                self.maxY = ceil(max(coordinateYUser1, self.maxY))
                self.maxY = ceil(max(coordinateYUser2, self.maxY))
                self.maxT = max(time, self.maxT)

    def get_line(self, line):
        l = line.strip().split(" ")
        return [int(l[0]), float(l[1]), float(l[2]), float(l[3])]

    def parse_raw(self, filename):
        self.preParseRaw(filename)
        cells = {}

        g = Graph()
        position_dict = {}
        beginning_positions = {}
        bar = Bar(self.filesize, "Parsing RAW file")

        with open(self.generateFileName(filename), "w+") as out, \
             open(filename, "r") as entrada:
            new_lines = 0
            for i, line in enumerate(entrada):
                bar.progress()
                _id, posx, posy, time = self.get_line(line)

                #comps = line.split(" ")
                #_id = int(comps[0])
                #posx, posy = float(comps[1]), float(comps[2])
                coordx, coordy = floor(posx/self.r), floor(posy/self.r)
                #time = float(comps[3])

                user = User(_id, posx, posy)
                u1 = str(user)
                u1x, u1y = user.x, user.y

                # This block adds a user to the map
                if u1 not in position_dict:
                    e = PositionEntry(posx, posy, coordx, coordy, time)
                    position_dict[u1] = e
                    g.add_vertex(u1)
                    new_cell = str(Cell(coordx, coordy))

                    if new_cell not in cells:
                        cells[new_cell] = []
                    cells[new_cell].append(user)

                # If the uses is already added, this block checks its location
                else:
                    entry = position_dict[u1]
                    entryx, entryy = entry.positionX, entry.positionY

                    if entryx != posx or entryy != posy:
                        # The node moved
                        old_cell = str(Cell(entry.coordX, entry.coordY))

                        users_in_cell = cells[old_cell]
                        users_in_cell = self.removeUserFromCell(users_in_cell,
                            u1)

                        cells[old_cell] = users_in_cell

                        old_user = User(_id, entryx, entryy)

                        new_cell = str(Cell(coordx, coordy))
                        if new_cell not in cells:
                            cells[new_cell] = []
                        cells[new_cell].append(user)

                    del position_dict[u1]
                        # Why checking the dist if its already inside the radius?
                        # This step is repeating the step below
                        # Its possibly adding the same contacts repeated

                #After adding or updating user, this block adds contacts
                for c in cells.keys():
                    users_in_cell = cells[c]
                    for user2 in users_in_cell:
                        u2 = str(user2)
                        u2x, u2y = user2.x, user2.y

                        if u1 != u2:
                            dist = self.euclidean(u1x, u1y, u2x, u2y)
                            e = Encounter(int(u1), int(u2))
                            e = str(e)
                            if dist <= self.r:
                                if not g.containsEdge(u1,u2):
                                    pos = "{} {} {} {}".format(u1x, u1y, u2x, u2y)
                                    beginning_positions[e] = pos
                                g.add_edge(u1, u2, time)
                                g.add_edge(u2, u1, time)

                            elif g.containsEdge(u1, u2):
                                begin = beginning_positions[e]
                                entry = self.generateEntry(user, user2,
                                    time, g, begin)
                                out.write(entry)
                                g.remove_edge(u1, u2)
                                g.remove_edge(u2, u1)
        bar.finish()

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
                    coordX = floor(posX / self.r)
                    coordY = floor(posY / self.r)
                    time = float(components[3])

                    user = User(_id, posX, posY)
                    u1 = str(user)
                    u1x, u1y = user.x, user.y

                    try:
                        entry = positionDictionary[u1]
                        entryX, entryY = entry.positionX, entry.positionY
                        if entryX != posX or entryY != posY:
                            # The node moved
                            oldCell = Cell(entry.coordX, entry.coordY)
                            usrInCell = cells[str(oldCell)]
                            usrInCell = self.removeUserFromCell(usrInCell, u1)
                            cells[str(oldCell)] = usrInCell
                            oldUser = User(_id, entryX, entryY)
                            r = self.r
                            adj = self.getAdjacentCellUsers(cells, oldUser, r)
                            newCell = Cell(coordX, coordY)
                            try:
                                usrInCell = cells[str(newCell)]
                                usrInCell.append(user)
                                cells[str(newCell)] = usrInCell
                            except:
                                usrInCell = []
                                usrInCell.append(user)
                                cells[str(newCell)] = usrInCell

                            for user2 in adjacent:
                                u2x, u2y = user2.x, user2.y
                                u2 = str(user2)
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
                                        enc = str(encounter)
                                        pos = str(u1x) + " " + str(u1y) + " "
                                        pos += str(u2x) + " " + str(u2y)
                                        beginingPositions[enc] = pos

                                elif (g.containsEdge(u1, u2)):
                                    encounter = Encounter(int(u1), int(u2))
                                    enc = str(encounter)
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
                            usersInCell = cells[str(newCell)]
                            usersInCell.append(user)
                            cells[str(newCell)] = usersInCell
                        except:
                            usersInCell = []
                            usersInCell.append(user)
                            cells[str(newCell)] = usersInCell

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
                                u1 = str(user)
                                u1x, u1y = user.x, user.y
                                usersInCell = cells[str(newCell)]
                                for user2 in usersInCell:
                                    u2 = str(user2)
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
                                                enc = str(e)
                                                pos = str(u1x) + " " + str(u1y)
                                                pos += " " + str(u2x) + " "
                                                pos += str(u2y)
                                                beginingPositions[enc] = pos
                                        elif (g.containsEdge(u1, u2)):
                                            e = Encounter(int(u1), int(u2))
                                            enc = str(e)
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
            if (str(user) == id):
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
        w = g.getEdgeWeight(str(user), str(user2))
        entry = "{} {} ".format(user.id, user2.id)
        entry += "{} {} {} ".format(time, w, (time - w))
        entry += "{}\n".format(beginingPosition)
        return entry

    def getAdjacentCellUsers(self, cells, user, r):
        adjacent = []

        k = floor(user.x / r)
        rangeXBegin = k - 1 if k - 1 > 0 else 0

        l = floor(user.x / r)
        rangeYBegin = l - 1 if l - 1 > 0 else 0

        while rangeXBegin <= k + 1:
            while rangeYBegin <= l + 1:
                newCell = Cell(rangeXBegin, rangeYBegin)
                if str(newCell) in cells:
                    usersInCell = cells[str(newCell)]
                    for u2 in usersInCell:
                        if (str(user) != str(u2)):
                            if self.euclidean(user.x, user.y, u2.x, u2.y) <= r:
                                adjacent.append(u2)
                rangeYBegin += 1
            rangeXBegin += 1
        return adjacent

    def euclidean(self, xi, yi, xj, yj):
        return sqrt(((xi - xj) ** 2) + ((yi - yj) ** 2))

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
