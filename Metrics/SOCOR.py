from Metrics.Metric import Metric
import numpy as np

class SOCOR(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.socor = 0
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID
        self.topo = kwargs.get("TOPO")
        self.edgep = kwargs.get("EDGEP")

    def print(self):
        with open(self.outfile, "w+") as out:
            out.write("{}\n".format(self.socor))

    @Metric.timeexecution
    def extract(self):
        topoValues = [x for x in self.topo.values()]
        edgepValues = [x for x in self.edgep.values()]

        stdTopo = np.std(topoValues)
        stdEdgep = np.std(edgepValues)

        cov = self.covariance()
        div = stdTopo * stdEdgep
        self.socor = cov/max(1, div)


    def covariance(self):
        cov = 0
        meanTopo = np.mean([x for x in self.topo.values()])
        meanEdgep = np.mean([x for x in self.edgep.values()])

        for key in self.topo.keys():
            t = self.topo[key]
            e = self.edgep[key]

            cov += (t - meanTopo) * (e - meanEdgep)

        cov /= len(self.topo.keys())
        return cov

    def commit(self):
        return {}

    def explain(self):
        return "SOCOR"
