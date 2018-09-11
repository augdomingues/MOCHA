"""
    This module extracts the Contact Entropy (CONEN) for each pair of
    contacts in the trace.
"""
import math
from Metrics.Metric import Metric

class CONEN(Metric):
    """ CONEN extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.conen = {}
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id

    def print(self):
        with open(self.outfile, "w") as out:
            for key, item in self.conen.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:

                comps = line.strip().split(" ")

                user1, user2 = comps[0], comps[1]

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
            for value in item.values():
                entropy += (value/summ) * math.log2((1/(value/summ)))
            self.conen[key] = entropy


    def explain(self):
        return "CONEN"

    def commit(self):
        return {}
