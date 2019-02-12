"""
    This module extracts the Center (CENTER) metric.
    The Center is the list of nodes with eccentricity equals
    to the graph RADIUS.
"""

from Metrics.Metric import Metric
import networkx as nx


class CENTER(Metric):
    """ CENTER extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.center = []
        self.graph = nx.Graph()
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id
        self.eccen = kwargs.get("eccen", None)

    def print(self):
        with open(self.outfile, "w+") as out:
            for node in self.center:
                out.write("{}\n".format(node))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split()
                user1, user2 = comps[0], comps[1]

                self.graph.add_node(user1)
                self.graph.add_node(user2)
                self.graph.add_edge(user1, user2)

        if self.eccen is None:
            try:
                self.eccen = nx.eccentricity(self.graph)
                self.center = nx.center()
            except BaseException:
                self.eccen["Any node"] = "infinity"
                self.center = []
                raise

    def commit(self):
        return {}

    def explain(self):
        return "CENTER"
