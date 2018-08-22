from Metrics.Metric import Metric

class MAXCON(Metric):

    def __init__(self, infile, outfile, reportID, **kwargs):
        self.maxcon = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID
        self.kwargs = kwargs

    def print(self):
        return "Not implemented."

    @Metric.timeexecution
    def extract(self):
        return "Not implemented."

    def explain(self):
        return "MAXCON"
