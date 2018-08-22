from Metrics.Metric import Metric
import math
from Encounter import Encounter

class EDGEP(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.edgep = {}
        self.encounters = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID

    def print(self):
        with open(self.outfile, 'w') as out:
            for key, item in self.edgep.items():
                if self.reportID:
                    user1, user2 = key.split(" ")
                    out.write("{},{},{}\n".format(user1, user2, item))
                else:
                    out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                encounterDay = int(math.floor(float(comps[3]) / 86400))
                encounter = Encounter(int(comps[0]), int(comps[1]))
                enc = encounter.toString()

                value = self.edgep.get(enc, 0)
                day = self.encounters.get(enc, -1)

                if day != encounterDay:
                    self.edgep[enc] = value + 1
                    self.encounters[enc] = encounterDay

    def commit(self):
        values = {"EDGEP": self.edgep}
        return values

    def explain(self):
        return "EDGEP"
