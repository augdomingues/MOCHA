"""
    This module extracts the Contact Duration (CODU) for all the
    pairs of contacts in the trace.
"""
from collections import defaultdict
from Metrics.Metric import Metric


class CODU(Metric):
    """ Contact Duration Extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.codu = defaultdict(list)
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id
        self.kwargs = kwargs

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.codu.items():
                for diff in item:
                    if self.report_id:
                        out.write("{},{},".format(key[0], key[1]))
                    out.write("{}\n".format(diff))

    def explain(self):
        return "CODU"

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]
                begin, end = float(comps[3]), float(comps[2])
                diff = end - begin

                self.codu[(user1, user2)].append(diff)

    def commit(self):
        return {}
