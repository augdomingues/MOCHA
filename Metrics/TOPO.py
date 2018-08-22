from Metrics.Metric import Metric
from Graph import Graph
from Encounter import Encounter

class TOPO(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.topo = {}
        self.graph = Graph()
        self.totalNeighbors = {}
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID


    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.topo.items():
                if self.reportID:
                    user1, user2 = key.split(" ")
                    out.write("{},{},".format(user1, user2))
                out.write("{}\n".format(item))

    @Metric.timeexecution
    def extract(self):
        with open(self.infile, "r") as inn:
            for line in inn:
                comps = line.strip().split(" ")
                user1, user2 = comps[0], comps[1]

                self.graph.add_vertex(user1)
                self.graph.add_vertex(user2)

                if not self.graph.containsEdge(user1, user2):
                    self.graph.add_edge(user1, user2)

        edges = self.graph.edgeSet()
        for edge in edges:
            src = edge.src
            trg = edge.target
            enc = Encounter(int(src), int(trg)).toString()


            if enc not in self.totalNeighbors:
                self.totalNeighbors[enc] = []

            neighborsSrc = self.graph.get_vertex(src).get_connections()
            degreeSrc = len(neighborsSrc)

            neighborsTrg = self.graph.get_vertex(src).get_connections()
            degreeDest = len(neighborsTrg)

            exists = 0
            if self.graph.containsEdge(src, trg):
                exists = 1

            to = 0
            for t in neighborsTrg:
                if t in neighborsSrc:
                    to += 1
            numerator = float(to) + 1
            denominator = ((degreeSrc - exists) + (degreeDest - exists) -to) +1
            if denominator == 0:
                denominator = 1

            toPct = numerator/denominator
            self.topo[enc] = toPct

    def commit(self):
        values = {"TOPO": self.topo}
        return values

    def explain(self):
        return "TOPO"
