from Metrics.Metric import Metric
from Graph import Graph
from Graph import Vertex
from Graph import Edge
from Encounter import Encounter

class INCO(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.inco = {}
        self.graph = Graph()
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.inco.items():
                if self.reportID:
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

                incoEncounters = []

                if self.graph.containsEdge(user1, user2):
                    enc = Encounter(int(user1), int(user2))
                    enc = enc.toString()
                    incoEncounters = self.inco[enc]
                    w = float(self.graph.getEdgeWeight(user1, user2))
                    incoEncounters.append(float(comps[2]) - float(w))
                    self.inco[enc].append(incoEncounters)

                    self.graph.add_edge(user1, user2, float(comps[3]))
                else:
                    self.graph.add_vertex(user1)
                    self.graph.add_vertex(user2)

                    encounter = Encounter(int(user1), int(user2))
                    encounter = encounter.toString()
                    self.inco[encounter] = []
                    self.graph.add_edge(user1, user2, float(comps[3]))

    def commit(self):
        return {}
