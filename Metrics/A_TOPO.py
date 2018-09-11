"""
    This module extracts the average Topological Overlap (TOPO) for
    every node in the trace.
"""
from Metrics.Metric import Metric
from Graph import Graph
from Mocha_utils import Encounter

class A_TOPO(Metric):
    """ Average TOPO extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.topo = {}
        self.a_topo = {}
        self.graph = Graph()
        self.total_neighbors = {}
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

                self.graph.add_vertex(user1)
                self.graph.add_vertex(user2)

                if not self.graph.contains_edge(user1, user2):
                    self.graph.add_edge(user1, user2)

        edges = self.graph.edge_set()
        for edge in edges:
            src = edge.src
            trg = edge.target
            enc = str(Encounter(int(src), int(trg)))


            if enc not in self.total_neighbors:
                self.total_neighbors[enc] = []

            neighbors_src = self.graph.get_vertex(src).get_connections()
            degree_src = len(neighbors_src)

            neighbors_trgt = self.graph.get_vertex(src).get_connections()
            degree_dest = len(neighbors_trgt)

            exists = 0
            if self.graph.contains_edge(src, trg):
                exists = 1

            to = 0
            for t in neighbors_trgt:
                if t in neighbors_src:
                    to += 1
            numerator = float(to) + 1
            denominator = ((degree_src - exists) + (degree_dest - exists) -to) +1
            if denominator == 0:
                denominator = 1

            toPct = numerator/denominator
            self.topo[enc] = toPct

        for key, item in self.topo.items():
            nodea, nodeb = key.split(" ")

            if nodea not in self.a_topo:
                self.a_topo[nodea] = []
            self.a_topo[nodea].append(item)

            if nodeb not in self.a_topo:
                self.a_topo[nodeb] = []
            self.a_topo[nodeb].append(item)

        for key, item in self.a_topo.items():
            self.a_topo[key] = sum(item)/max(len(item), 1)


    def commit(self):
        return {}

    def explain(self):
        return "Average TOPO"
