"""
    This module extracts the average Topological Overlap (TOPO) for
    every node in the trace.
"""
from collections import defaultdict
from Metrics.Metric import Metric
from mocha_utils import Encounter


class A_TOPO(Metric):
    """ Average TOPO extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.topo = {}
        self.a_topo = defaultdict(list)
        self.topologies = defaultdict(set)
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.a_topo.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]

                self.topologies[user1].add(user2)
                self.topologies[user2].add(user1)

        for source, source_neighbors in self.topologies.items():
            for target, target_neighbors in self.topologies.items():
                if source != target:
                    encounter = str(Encounter(source, target))

                    intersec = source_neighbors.intersection(target_neighbors)
                    intersec = len(intersec)

                    union = source_neighbors.union(target_neighbors)
                    union = len(union)

                    direct_connection = 1 if target in source_neighbors else 0

                    self.topo[encounter] = (intersec + direct_connection)/union

        for key, item in self.topo.items():
            nodea, nodeb = key.split(" ")

            self.a_topo[nodea].append(item)
            self.a_topo[nodeb].append(item)

        for key, item in self.a_topo.items():
            self.a_topo[key] = sum(item)/max(len(item), 1)

    def commit(self):
        return {}

    def explain(self):
        return "Average TOPO"
