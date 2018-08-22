from Metrics.Metric import Metric

class CODU(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.codu = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID
        self.kwargs = kwargs

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.codu.items():
                for diff in item:
                    if self.reportID:
                        out.write("{},{},".format(key[0], key[1]))
                    out.write("{}\n".format(diff))

    def explain(self):
        return "CODU"

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]
                begin, end = float(comps[3]), float(comps[2])
                diff = end - begin

                if (user1, user2) not in self.codu:
                    self.codu[(user1, user2)] = []
                self.codu[(user1, user2)].append(diff)


    def commit(self):
        return {}
