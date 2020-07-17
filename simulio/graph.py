class Node:
    def __init__(self, id, properties=None):
        self.id = id
        if properties is None:
            properties = {}
        self.properties = properties


class Edge:
    def __init__(self, from_id, to_id, properties=None):
        self.from_id = from_id
        self.to_id = to_id
        if properties is None:
            properties = {}
        self.properties = properties


class Graph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges


class BidirectionalRing(Graph):
    def __init__(self, n):
        nodes = []
        edges = []
        for i in range(n):
            nodes.append(Node(i))
            edges.append(Edge(i, (i + 1) % n))
            # edges.append(Edge(i, (i + n - 1) % n))  # (i-1) % n == (i+n-1) % n
        super().__init__(nodes, edges)
