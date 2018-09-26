"""
    This module extracts the Topological Overlap (TOPO) from all
    the pair of contacts in the trace.
"""
from Metrics.Metric import Metric
from mocha_utils import Encounter

class TOPO(Metric):
    """ TOPO extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.topo = {}
        self.topologies = {}
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id


    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.topo.items():
                if self.report_id:
                    user1, user2 = key.split(" ")
                    out.write("{},{},".format(user1, user2))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]

                if user1 not in self.topologies:
                    self.topologies[user1] = set()
                self.topologies[user1].add(user2)

                if user2 not in self.topologies:
                    self.topologies[user2] = set()
                self.topologies[user2].add(user1)

        for source, source_neighbors in self.topologies.items():
            for target, target_neighbors in self.topologies.items():
                if source != target:
                    encounter = str(Encounter(source, target))

                    intersec = source_neighbors.intersection(target_neighbors)
                    intersec = len(intersec)

                    # Passes if there is no intersection, ie topo is 0
                    if intersec == 0:
                        continue

                    union = source_neighbors.union(target_neighbors)
                    union = len(union)

                    direct_connection = 1 if target in source_neighbors else 0

                    self.topo[encounter] = (intersec + direct_connection)/union

    def commit(self):
        values = {"TOPO": self.topo}
        return values

    def explain(self):
        return "TOPO"
