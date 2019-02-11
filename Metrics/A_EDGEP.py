"""
    This module extracts the average Edge Persistence (EDGEP) for each
    node in the graph.
"""
import math
from collections import defaultdict
from Metrics.Metric import Metric
from mocha_utils import Encounter


class A_EDGEP(Metric):
    """ Average EDGEP extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.edgep = defaultdict(int)
        self.a_edgep = defaultdict(list)
        self.encounters = {}
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id

    def print(self):
        with open(self.outfile, 'w') as out:
            for key, item in self.a_edgep.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                encounter_day = int(math.floor(float(comps[3]) / 86400))
                encounter = Encounter(comps[0], comps[1])
                enc = str(encounter)

                day = self.encounters.get(enc, -1)

                if day != encounter_day:
                    self.edgep[enc] += 1
                    self.encounters[enc] = encounter_day

        for key, item in self.edgep.items():
            nodea, nodeb = key.split(" ")

            self.a_edgep[nodea].append(item)
            self.a_edgep[nodeb].append(item)

        for key, item in self.a_edgep.items():
            self.a_edgep[key] = sum(item)/max(len(item), 1)

    def commit(self):
        return {}

    def explain(self):
        return "Average EDGEP"
