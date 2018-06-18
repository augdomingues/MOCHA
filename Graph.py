"""
      
     ( (
     _)_)_
   c(  M  )     MOCHA: a tool for MObility CHaracteristics Analysis
   ,-\___/-.
   `-------'


"""
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
    def __init__(self, src, target, weight=0):
        self.src = src
        self.target = target
        self.weight = weight

    def get_weight(self):
        return self.weight

class Graph:
    def __init__(self):
        self.vert_dict = {}
        #self.edges = []
        self.edges = {}

    def add_vertex(self, node):
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        return self.vert_dict[n]

    def remove_edge(self,frm,to):
        if (frm, to) in self.edges:
            del self.edges[((frm,to))]

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        if (frm,to) not in self.edges:
            edge = Edge(frm,to,cost)
            self.edges[(frm,to)] = edge

        #if not self.containsEdge(frm, to):
        #    edge = Edge(frm, to)
        #    self.edges.append(edge)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

    
    """
        containsEdge: checks if the graph has an edge between node user1 and user2
        params:
            user1: origin node (frm)
            user2: destination node (to)
        returns:
            True if exists; False otherwise
    """
    def containsEdge(self, user1, user2):
        return (user1,user2) in self.edges
    
    
    
    """
        getEdgeWeight: returns the weight of the edge
        params:
            user1: origin node (frm)
            user2: destination node (to)
        returns:
            edge weight if existent; -1 otherwise
    """
    def getEdgeWeight(self, user1, user2):
        if self.containsEdge(user1,user2):
            return self.edges[(user1,user2)].get_weight()
        else:
            return -1

    """
        edgeSet: returns a vector containing all the edges
        params:
            
        returns:
            a vector containing all the edges
    """
    def edgeSet(self):
        return [item for item in self.edges.values()]
