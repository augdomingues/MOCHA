"""
    This module extracts the Radius (RADIUS) of a graph.
    The radius of a graph is defined as the minimum
    eccentricity (ECCEN).
"""

from Metrics.Metric import Metric


class RADIUS(Metric):
    """ RADIUS extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.radius = {}
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id
        self.eccen = kwargs.get("eccen", None)

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.eccen.items():
                if self.report_id:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        if self.eccen is None:
            print("Missing ECCEN data.")
            return

        key = min(self.eccen)
        value = self.eccen[key]
        self.radius[key] = value

    def commit(self):
        values = {}
        return values

    def explain(self):
        return "RADIUS"
