"""
    This module extracts the Eccentricity (ECCEN)
    of all nodes in the graph. The eccentricity
    of a node v is defined as the maximum distance
    from v to all nodes in G
"""

from Metrics.Metric import Metric
import networkx as nx


class ECCEN(Metric):
    """ ECCEN extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.eccen = {}
        self.graph = nx.Graph()
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.eccen.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split()
                user1, user2 = comps[0], comps[1]

                self.graph.add_node(user1)
                self.graph.add_node(user2)
                self.graph.add_edge(user1, user2)
        try:
            self.eccen = nx.eccentricity(self.graph)
        except BaseException:
            self.eccen["Any node"] = "infinity"
            raise

    def commit(self):
        values = {"eccen": self.eccen}
        return values

    def explain(self):
        return "ECCEN"
