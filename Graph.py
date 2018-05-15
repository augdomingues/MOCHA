class Vertex:
    def __init__(self, node):
        self.id = node
        self.adjacent = {}

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

class Edge:
    def __init__(self, src, target):
        self.src = src
        self.target = target

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.edges = []

    def add_vertex(self, node):
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        return self.vert_dict[n]

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        if not self.containsEdge(frm, to):
            edge = Edge(frm, to)
            self.edges.append(edge)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

    def containsEdge(self, user1, user2):
        try:
            a = self.get_vertex(user1)
            a = self.get_vertex(user2)
        except:
            return False

        vert1 = self.get_vertex(user1)
        try:
            for vert2 in vert1.get_connections():
                if vert2.get_id() == user2:
                    return True
        except:
            pass
        return False

    def getEdgeWeight(self, user1, user2):
        u1 = self.get_vertex(user1)
        u2 = self.get_vertex(user2)

        try:
            return u2.get_weight(u1)
        except:
            return 0

    def edgeSet(self):
        return self.edges


