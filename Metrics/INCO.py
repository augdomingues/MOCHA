"""
    This module extract the Inter-contact duration (INCO) metric for
    each pair of contacts in the trace.
"""
from Metrics.Metric import Metric
import networkx as nx
from mocha_utils import Encounter


class INCO(Metric):
    """ INCO extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.inco = {}
        self.graph = nx.Graph()
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.inco.items():
                if self.report_id:
                    user1, user2 = key.split(" ")
                    out.write("{},{},".format(user1, user2))
                for value in item:
                    out.write("{}\n".format(value))

    def explain(self):
        return "INCO"

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]

                inco_encounters = []

                if self.graph.has_edge(user1, user2):
                    enc = Encounter(user1, user2)
                    enc = str(enc)
                    inco_encounters = self.inco[enc]
                    weight = float(self.graph[user1][user2]["weight"])
                    inco_encounters.append(float(comps[2]) - float(weight))
                    self.inco[enc] = inco_encounters

                    self.graph.add_edge(user1, user2, weight=float(comps[3]))
                else:
                    self.graph.add_node(user1)
                    self.graph.add_node(user2)

                    encounter = Encounter(user1, user2)
                    encounter = str(encounter)
                    self.inco[encounter] = []
                    self.graph.add_edge(user1, user2, weight=float(comps[3]))

    def commit(self):
        return {}
