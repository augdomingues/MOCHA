"""
    Extracts the average Contact Duration (CODU) for each node.

"""
from Metrics.Metric import Metric

class A_CODU(Metric):
    """ Average CODU extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.codu = {}
        self.a_codu = {}
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id
        self.kwargs = kwargs

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.a_codu.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    def explain(self):
        return "Average CODU"

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]
                begin, end = float(comps[3]), float(comps[2])
                diff = end - begin

                if user1 not in self.a_codu:
                    self.a_codu[user1] = []
                self.a_codu[user1].append(diff)

                if user2 not in self.a_codu:
                    self.a_codu[user2] = []
                self.a_codu[user2].append(diff)

        for key, item in self.a_codu.items():
            self.a_codu[key] = sum(item)/max(len(item), 1)

    def commit(self):
        return {}
