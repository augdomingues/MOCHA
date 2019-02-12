"""
    This module is responsible for parsing an input trace.
    It parses the trace by creating a new trace, that contains
    informations about contacts that happened during the collection.
    This output trace possess a defined format which is used
    to extract the metrics in the subsequent steps.

"""
from math import ceil
from operator import itemgetter
import os
from mocha_utils import (
    Encounter,
    PositionReport
)
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
        output_file = self.generate_filename(filename)
        with open(output_file, 'w') as out:
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
        return output_file

    def remove_empty(self, components):
        """ Remove empty fields in the line. """
        return [c for c in components if c != ""]

    def pre_parse_raw(self, filename):
        """ Prepare a raw trace to be parsed. """

        last_reported_time = -1

        with open(filename, 'r') as entrada:
            print("Pre parsing...", end="")
            for line in entrada:

                self.filesize += 1
                components = line.split(" ")
                coordinateX = float(components[1])
                coordinateY = float(components[2])
                time = float(components[3])

                if time < last_reported_time:
                    print(" Error. Unsorted trace!")
                    raise SystemError(0)

                last_reported_time = time

                self.maxT = int(max(time, self.maxT))
                self.maxX = int(ceil(max(coordinateX, self.maxX)))
                self.maxY = int(ceil(max(coordinateY, self.maxY)))

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
        line = line.strip().split(" ")
        return [line[0],
                float(line[1]),
                float(line[2]),
                float(line[3])]

    def naive_raw(self, filename):
        """ Parse a raw trace not considering the cells. """
        self.pre_parse_raw(filename)

        radius = self.r
        contacts = dict()
        positions = dict()

        output_filename = self.generate_filename(filename)
        with open(output_filename, "w+") as saida, \
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
        return output_filename

    def generate_filename(self, filename):
        """ Generates the filename for the parsed trace. """

        filename = os.path.abspath(filename)
        if "." in filename:
            name, extension = filename.split(".")[0], filename.split(".")[1]
            filename = "{}_parsed.{}".format(name, extension)
        else:
            filename = "{}_parsed".format(filename)

        if os.path.exists(filename):
            overwrite = input("\nFile already exists. Overwrite it? (y/n): ")
            overwrite = overwrite.upper()
            if overwrite not in ["TRUE", "Y", "YES"]:
                raise SystemExit(0)

        return filename
