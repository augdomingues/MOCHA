import math
from collections import defaultdict
from Metrics.Metric import Metric


class MAXCON(Metric):

    def __init__(self, infile, outfile, reportID, **kwargs):
        self.maxcon = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID
        self.kwargs = kwargs

    def print(self):
        with open(self.outfile, "w") as out:
            for key, item in self.maxcon.items():
                if self.reportID:
                    user = key
                    out.write("{},".format(user))
                user_maxcon = max([v for k, v in item.items()])
                out.write("{}\n".format(user_maxcon))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")

                encounter_day = int(math.floor(float(comps[3]) / 86400))

                node_1, node_2 = comps[0], comps[1]
                if node_1 not in self.maxcon:
                    self.maxcon[node_1] = defaultdict(int)
                if node_2 not in self.maxcon:
                    self.maxcon[node_2] = defaultdict(int)

                self.maxcon[node_1][encounter_day] += 1
                self.maxcon[node_2][encounter_day] += 1

    def commit(self):
        values = {"MAXCON": self.maxcon}
        return values

    def explain(self):
        return "MAXCON - Maximum number of connections in a day per node"
