"""
    This module is responsible for parsing an input trace.
    It parses the trace by creating a new trace, that contains
    informations about contacts that happened during the collection.
    This output trace possess a defined format which is used
    to extract the metrics in the subsequent steps.

"""
from math import floor, ceil, sqrt
from operator import itemgetter
import os
from mocha_utils import (
    Encounter,
    PositionEntry,
    PositionReport,
    Cell,
    User
)
from Graph import Graph
from Bar import Bar


class Parser:

    def __init__(self, r):
        """ Init the class values. """
        self.r = r
        self.maxX = 0
        self.maxY = 0
        self.maxT = 0
        self.filesize = 0
        self.parsedfilesize = 0

    def parse_swim(self, filename):
        """ Parse a SWIM trace. """
        self.collect_maxes_swim(filename)
        newFile = self.generate_filename(filename)
        with open(newFile, 'w') as out:
            encounters = {}
            bar = Bar(self.filesize, "Parsing SWIM file")
            with open(filename, 'r') as entrada:
                for i, line in enumerate(entrada):
                    bar.progress()
                    comps = line.strip().split(" ")
                    comps = self.remove_empty(comps)
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

    def remove_empty(self, components):
        """ Remove empty fields in the line. """
        return [c for c in components if c != ""]

    def pre_parse_raw(self, filename):
        """ Prepare a raw trace to be parsed. """
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

    def collect_maxes(self, filename):
        """ Collect the maxes from a RAW trace. """
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

    def collect_maxes_swim(self, filename):
        """ Collect the maximum values for a SWIM trace. """
        with open(filename, 'r') as entrada:
            for line in entrada:

                self.filesize += 1
                components = line.split(" ")
                components = self.remove_empty(components)

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
        """ Reads and formats a line from the input trace. """
        l = line.strip().split(" ")
        return [int(l[0]), float(l[1]), float(l[2]), float(l[3])]

    def naive_raw(self, filename):
        """ Parse a raw trace not considering the cells. """
        radius = self.r
        contacts = dict()
        positions = dict()
        self.pre_parse_raw(filename)
        with open(self.generate_filename(filename), "w+") as saida, \
             open(filename, "r") as entrada:

            bar = Bar(self.filesize, "Parsing RAW file")
            for i, line in enumerate(entrada):
                bar.progress()
                _id, x, y, time = self.get_line(line)

                if _id not in contacts:
                    contacts[_id] = dict()

                node_position = PositionReport(x, y, time)
                positions[_id] = node_position

                for other_id, item in positions.items():
                    if other_id != _id:
                        contact_exists = other_id in contacts[_id]
                        contact_exists = contact_exists or _id in contacts[other_id]

                        # Beginning a new contact
                        if node_position - item <= radius and not contact_exists:
                            contacts[_id][other_id] = (time, x, y, item.x, item.y)
                            contacts[other_id][_id] = (time, item.x, item.y, x, y)

                        # Ending an existing contact
                        elif node_position - item > radius and contact_exists:
                            c = contacts[_id][other_id]
                            begin, begin_x, begin_y, begin_xo, begin_yo = c

                            duration = time - begin

                            s = "{} {} ".format(_id, other_id)
                            s += "{} {} {} ".format(time, begin, duration)
                            s += "{} {} ".format(begin_x, begin_y)
                            s += "{} {}\n".format(begin_xo, begin_yo)
                            saida.write(s)

                            del contacts[_id][other_id]
                            del contacts[other_id][_id]

            # At this point, the trace has ended, but we still need to close
            # open contacts.

            # We add to a vector to sort by starting time
            last_contacts = []
            # We dont want to modify the dict while parsing it, so:
            reported = dict()
            for _id, contact in contacts.items():
                for other_id, report in contact.items():

                    if (_id, other_id) not in reported:
                        begin, begin_x, begin_y, begin_xo, begin_yo = report

                        duration = time - begin

                        s = "{} {} ".format(_id, other_id)
                        s += "{} {} {} ".format(time, begin, duration)
                        s += "{} {} ".format(begin_x, begin_y)
                        s += "{} {}\n".format(begin_xo, begin_yo)
                        last_contacts.append((s, begin))

                        reported[(_id, other_id)] = True
                        reported[(other_id, _id)] = True

            last_contacts = sorted(last_contacts, key=itemgetter(1))

            for lc in last_contacts:
                saida.write(lc[0])
        bar.finish()

    def parse_raw(self, filename):
        """ Parse a raw trace considering the cells. """
        self.pre_parse_raw(filename)
        cells = {}
        g = Graph()
        positionDictionary = {}
        beginingPositions = {}
        with open(self.generate_filename(filename), 'w+') as out:
            newLines = 0
            bar = Bar(self.filesize, "Parsing RAW file")
            with open(filename) as entrada:
                for _, line in enumerate(entrada):
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
                            usrInCell = self.remove_user_from_cell(usrInCell, u1)
                            cells[str(oldCell)] = usrInCell
                            oldUser = User(_id, entryX, entryY)
                            r = self.r
                            adj = self.get_adjacent_cell_users(cells, oldUser, r)
                            newCell = Cell(coordX, coordY)
                            try:
                                usrInCell = cells[str(newCell)]
                                usrInCell.append(user)
                                cells[str(newCell)] = usrInCell
                            except:
                                usrInCell = []
                                usrInCell.append(user)
                                cells[str(newCell)] = usrInCell

                            for user2 in adj:
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

                                elif g.contains_edge(u1, u2):
                                    encounter = Encounter(int(u1), int(u2))
                                    enc = str(encounter)
                                    beginPos = beginingPositions[enc]
                                    out.write(self.generate_entry(user, user2,
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

                    rangex_begin = 0
                    if coordX - 1 > 0:
                        rangex_begin = coordX - 1

                    rangey_begin = 0
                    if coordY - 1 > 0:
                        rangey_begin = coordY - 1

                    while rangex_begin <= coordX + 1:
                        while rangey_begin <= coordY + 1:
                            newCell = Cell(rangex_begin, rangey_begin)
                            try:
                                u1 = str(user)
                                u1x, u1y = user.x, user.y
                                usersInCell = cells[str(newCell)]
                                for user2 in usersInCell:
                                    u2 = str(user2)
                                    u2x, u2y = user2.x, user2.y
                                    if u1 != u2:
                                        eu = self.euclidean(u1x, u1y, u2x, u2y)
                                        if eu <= self.r:
                                            if g.contains_edge(u1, u2):
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
                                        elif g.contains_edge(u1, u2):
                                            e = Encounter(int(u1), int(u2))
                                            enc = str(e)
                                            beginPos = beginingPositions[enc]
                                            out.write(self.generate_entry(user,
                                                                          user2, time,
                                                                          g, beginPos))
                                            newLines += 1
                                            g.remove_edge(u1, u2)
                                            g.remove_edge(u2, u1)
                            except:
                                pass
                            rangey_begin += 1

                        if coordX - 1 > 0:
                            rangey_begin = coordY - 1
                        else:
                            rangey_begin = 0
                        rangex_begin += 1

        self.filesize = newLines
        bar.finish()
        return self.generate_filename(filename)

    def remove_user_from_cell(self, usersInCell, id):
        """ Removes the user from its cell. """
        toBeRemoved = User(0, 0, 0)
        for user in usersInCell:
            if str(user) == id:
                toBeRemoved = user
        usersInCell.remove(toBeRemoved)
        return usersInCell

    def generate_filename(self, filename):
        """ Generates the filename for the parsed trace. """
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

    def generate_entry(self, user, user2, time, g, beginingPosition):
        """ Formats an entry to the output file. """
        w = g.get_edge_weight(str(user), str(user2))
        entry = "{} {} ".format(user.id, user2.id)
        entry += "{} {} {} ".format(time, w, (time - w))
        entry += "{}\n".format(beginingPosition)
        return entry

    def get_adjacent_cell_users(self, cells, user, r):
        """ Get the users in the adjacent cell. """
        adjacent = []

        k = floor(user.x / r)
        rangex_begin = k - 1 if k - 1 > 0 else 0

        l = floor(user.x / r)
        rangey_begin = l - 1 if l - 1 > 0 else 0

        while rangex_begin <= k + 1:
            while rangey_begin <= l + 1:
                newCell = Cell(rangex_begin, rangey_begin)
                if str(newCell) in cells:
                    usersInCell = cells[str(newCell)]
                    for u2 in usersInCell:
                        if str(user) != str(u2):
                            if self.euclidean(user.x, user.y, u2.x, u2.y) <= r:
                                adjacent.append(u2)
                rangey_begin += 1
            rangex_begin += 1
        return adjacent

    def euclidean(self, coord_xi, coord_yi, coord_xj, coord_yj):
        """ Computes the euclidean distance. """
        return sqrt(((coord_xi - coord_xj) ** 2) + ((coord_yi - coord_yj) ** 2))
