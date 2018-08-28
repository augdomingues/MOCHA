class Vertex:
    """ Class that represents a node (Vertex) in the graph. """
    def __init__(self, node):
        self.id = node
        self.adjacent = {}

    def add_neighbor(self, neighbor, weight=0):
        """ Add neighbor to node. """
        self.adjacent[neighbor] = weight

    def get_connections(self):
        """ Return node connections. """
        return self.adjacent.keys()

    def get_id(self):
        """ Return node ID. """
        return self.id

    def get_weight(self, neighbor):
        """ Return weight of edge between node and neighbor. """
        return self.adjacent[neighbor]


class Edge:
    """ Class that represents an edge in the graph. """
    def __init__(self, src, target, weight=0):
        self.src = src
        self.target = target
        self.weight = weight

    def get_weight(self):
        return self.weight


class Graph:
    """ Class that represents a graph structure. """
    def __init__(self):
        self.vert_dict = {}
        self.edges = {}

    def add_vertex(self, node):
        """ Adds a new node to the graph. """
        new_vertex = Vertex(node)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        """ Return a given node n. """
        return self.vert_dict[n]

    def remove_edge(self, frm, to):
        """  Remove edge between two nodes. """
        if (frm, to) in self.edges:
            del self.edges[((frm, to))]

    def add_edge(self, frm, to, cost=0):
        """ Add weighted edge between two nodes. """
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        if (frm, to) not in self.edges:
            edge = Edge(frm, to, cost)
            self.edges[(frm, to)] = edge

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        """ Returns the set of nodes in the graph. """
        return self.vert_dict.keys()

    def containsEdge(self, user1, user2):
        """
            containsEdge: checks if the graph has edge between node user1 and user2
            params:
                user1: origin node (frm)
                user2: destination node (to)
            returns:
                True if exists; False otherwise
        """
        return (user1, user2) in self.edges

    def getEdgeWeight(self, user1, user2):
        """
            getEdgeWeight: returns the weight of the edge
            params:
                user1: origin node (frm)
                user2: destination node (to)
            returns:
                edge weight if existent; -1 otherwise
        """
        if self.containsEdge(user1, user2):
            return self.edges[(user1, user2)].get_weight()
        else:
            return -1

    def edgeSet(self):
        """
            edgeSet: returns a vector containing all the edges
            params:

            returns:
                a vector containing all the edges
        """
        return [item for item in self.edges.values()]

