"""
    This module extracts the Edge persistence (EDGEP) for
    each pair of contacts in the trace.

"""
import math
from Metrics.Metric import Metric
from mocha_utils import Encounter

class EDGEP(Metric):
    """ EDGEP extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.edgep = {}
        self.encounters = {}
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id

    def print(self):
        with open(self.outfile, 'w') as out:
            for key, item in self.edgep.items():
                if self.report_id:
                    user1, user2 = key.split(" ")
                    out.write("{},{},".format(user1, user2))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                encounter_day = int(math.floor(float(comps[3]) / 86400))
                encounter = Encounter(comps[0], comps[1])
                enc = str(encounter)

                value = self.edgep.get(enc, 0)
                day = self.encounters.get(enc, -1)

                if day != encounter_day:
                    self.edgep[enc] = value + 1
                    self.encounters[enc] = encounter_day

    def commit(self):
        values = {"EDGEP": self.edgep}
        return values

    def explain(self):
        return "EDGEP"
