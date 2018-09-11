"""
    This module extracts the Social correlation (SOCOR) of a trace.
"""
import numpy as np
from Metrics.Metric import Metric

class SOCOR(Metric):
    """ SOCOR extraction class. """

    def __init__(self, infile, outfile, report_id, **kwargs):
        self.socor = 0
        self.infile = infile
        self.outfile = outfile
        self.report_id = report_id
        self.topo = kwargs.get("TOPO")
        self.edgep = kwargs.get("EDGEP")

    def print(self):
        with open(self.outfile, "w+") as out:
            out.write("{}\n".format(self.socor))

    @Metric.timeexecution
    def extract(self):
        topo_values = [x for x in self.topo.values()]
        edgep_values = [x for x in self.edgep.values()]

        std_topo = np.std(topo_values)
        std_edgep = np.std(edgep_values)

        cov = self.covariance()
        div = std_topo * std_edgep
        self.socor = cov/max(1, div)


    def covariance(self):
        """ Calculates the covariance between two variables. """
        cov = 0
        mean_topo = np.mean([x for x in self.topo.values()])
        mean_edgep = np.mean([x for x in self.edgep.values()])

        for key in self.topo.keys():
            topo_value = self.topo[key]
            edgep_value = self.edgep[key]

            cov += (topo_value - mean_topo) * (edgep_value - mean_edgep)

        cov /= len(self.topo.keys())
        return cov

    def commit(self):
        return {}

    def explain(self):
        return "SOCOR"
