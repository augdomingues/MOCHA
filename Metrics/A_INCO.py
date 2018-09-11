from Metrics.Metric import Metric
from Graph import Graph
from Graph import Vertex
from Graph import Edge
from Mocha_utils import Encounter

class A_INCO(Metric):


    def __init__(self, infile, outfile, reportID, **kwargs):
        self.inco = {}
        self.a_inco = {}
        self.graph = Graph()
        self.infile = infile
        self.outfile = outfile
        self.reportID = reportID

    def print(self):
        with open(self.outfile, "w+") as out:
            for key, item in self.a_inco.items():
                if self.reportID:
                    out.write("{},".format(key))
                out.write("{}\n".format(item))

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
                    enc = str(enc)
                    incoEncounters = self.inco[enc]
                    w = float(self.graph.getEdgeWeight(user1, user2))
                    incoEncounters.append(float(comps[2]) - float(w))
                    self.inco[enc] = incoEncounters

                    self.graph.add_edge(user1, user2, float(comps[3]))
                else:
                    self.graph.add_vertex(user1)
                    self.graph.add_vertex(user2)

                    encounter = Encounter(int(user1), int(user2))
                    encounter = str(encounter)
                    self.inco[encounter] = []
                    self.graph.add_edge(user1, user2, float(comps[3]))

        for key, item in self.inco.items():
            nodea, nodeb = key.split(" ")

            if nodea not in self.a_inco:
                self.a_inco[nodea] = []
            self.a_inco[nodea] += item

            if nodeb not in self.a_inco:
                self.a_inco[nodeb] = []
            self.a_inco[nodeb] += item

        for key, item in self.a_inco.items():
            self.a_inco[key] = sum(item)/max(len(item), 1)

    def commit(self):
        return {}

