from Metrics.Metric import Metric
import math
from Mocha_utils import Encounter

class A_EDGEP(Metric):

    def __init__(self, infile, outfile, reportID, **kwargs):
        self.edgep = {}
        self.a_edgep = {}
        self.encounters = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID

    def print(self):
        with open(self.outfile, 'w') as out:
            for key, item in self.a_edgep.items():
                if self.reportID:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                encounterDay = int(math.floor(float(comps[3]) / 86400))
                encounter = Encounter(int(comps[0]), int(comps[1]))
                enc = str(encounter)

                value = self.edgep.get(enc, 0)
                day = self.encounters.get(enc, -1)

                if day != encounterDay:
                    self.edgep[enc] = value + 1
                    self.encounters[enc] = encounterDay

        for key, item in self.edgep.items():
            nodea, nodeb = key.split(" ")

            if nodea not in self.a_edgep:
                self.a_edgep[nodea] = []
            self.a_edgep[nodea].append(item)

            if nodeb not in self.a_edgep:
                self.a_edgep[nodeb] = []
            self.a_edgep[nodeb].append(item)

        for key, item in self.a_edgep.items():
            self.a_edgep[key] = sum(item)/max(len(item), 1)


    def commit(self):
        return {}

    def explain(self):
        return "Average EDGEP"
