from Metrics.Metric import Metric
import math

class CONEN(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.conen = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID

    def print(self):
        with open(self.outfile, "w") as out:
            for key, item in self.conen.items():
                if self.reportID:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:

                comps = line.strip().split(" ")

                user1, user2 = comps[0], comps[1]
                user1X, user1Y = float(comps[5]), float(comps[6])
                user2X, user2Y = float(comps[7]), float(comps[8])

                time = float(comps[4])

                if user1 in self.conen:
                    value = self.conen[user1].get(user2, 0)
                    self.conen[user1][user2] = value + 1
                else:
                    self.conen[user1] = {}

                if user2 in self.conen:
                    value = self.conen[user2].get(user1, 0)
                    self.conen[user2][user1] = value + 1
                else:
                    self.conen[user2] = {}

        for key, item in self.conen.items():
            summ = sum(item.values())
            summ = max(summ, 1)
            entropy = 0
            for v in item.values():
                entropy += (v/summ) * math.log2((1/(v/summ)))
            self.conen[key] = entropy


    def explain(self):
        return "CONEN"

    def commit(self):
        return {}
