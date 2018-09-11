"""
    Module that contains the implementation of a graphic.
    Will soon be replaced by networkx.
"""


class Vertex:
    """ Class that represents a node (Vertex) in the graph. """
    def __init__(self, node):
        """ Initiates vertex structures. """
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
        """ Return edge weight. """
        return self.weight

    def set_weight(self, weight):
        """ Set new edge weight. """
        self.weight = weight


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

    def get_vertex(self, node):
        """ Return a given node n. """
        return self.vert_dict[node]

    def remove_edge(self, origin, destiny):
        """  Remove edge between two nodes. """
        if (origin, destiny) in self.edges:
            del self.edges[((origin, destiny))]

    def add_edge(self, origin, destiny, cost=0):
        """ Add weighted edge between two nodes. """
        if origin not in self.vert_dict:
            self.add_vertex(origin)
        if destiny not in self.vert_dict:
            self.add_vertex(destiny)

        if (origin, destiny) not in self.edges:
            edge = Edge(origin, destiny, cost)
            self.edges[(origin, destiny)] = edge

        self.vert_dict[origin].add_neighbor(self.vert_dict[destiny], cost)
        self.vert_dict[destiny].add_neighbor(self.vert_dict[origin], cost)

    def get_vertices(self):
        """ Returns the set of nodes in the graph. """
        return self.vert_dict.keys()

    def contains_edge(self, user1, user2):
        """
            contains_edge: checks if the graph has edge between node user1 and user2
            params:
                user1: origin node (frm)
                user2: destination node (to)
            returns:
                True if exists; False otherwise
        """
        return (user1, user2) in self.edges

    def get_edge_weight(self, user1, user2):
        """
            get_edge_weight: returns the weight of the edge
            params:
                user1: origin node (frm)
                user2: destination node (to)
            returns:
                edge weight if existent; -1 otherwise
        """
        if self.contains_edge(user1, user2):
            return self.edges[(user1, user2)].get_weight()
        return -1

    def edge_set(self):
        """
            edge_set: returns a vector containing all the edges
            params:
            returns:
                a vector containing all the edges
        """
        return [item for item in self.edges.values()]
