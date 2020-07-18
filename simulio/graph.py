class Node:
    def __init__(self, id, properties=None):
        self.id = id
        if properties is None:
            properties = {}
        self.properties = properties

    def to_dict(self):
        return {
            'id': self.id,
            'properties': self.properties,
        }


class Edge:
    def __init__(self, from_id, to_id, properties=None):
        self.from_id = from_id
        self.to_id = to_id
        if properties is None:
            properties = {}
        self.properties = properties

    def to_dict(self):
        return {
            'from': self.from_id,
            'to': self.to_id,
            'properties': self.properties,
        }


class Graph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges

    def to_dict(self):
        return {
            'nodes': [node.to_dict() for node in self.nodes],
            'edges': [edge.to_dict() for edge in self.edges],
        }


class UnidirectionalRing(Graph):
    def __init__(self, n):
        nodes = []
        edges = []
        for i in range(n):
            nodes.append(Node(i))
            edges.append(Edge(i, (i + 1) % n))
        super().__init__(nodes, edges)


class BidirectionalRing(Graph):
    def __init__(self, n):
        nodes = []
        edges = []
        for i in range(n):
            nodes.append(Node(i))
            edges.append(Edge(i, (i + 1) % n))
            edges.append(Edge(i, (i + n - 1) % n))  # (i-1) % n == (i+n-1) % n
        super().__init__(nodes, edges)


class CompleteGraph(Graph):
    def __init__(self, n):
        nodes = []
        edges = []
        for i in range(n):
            nodes.append(Node(i))
            for j in range(n):
                if i != j:
                    edges.append(Edge(i, j))
        super().__init__(nodes, edges)


class ArbitraryGraph(Graph):
    def __init__(self, graph_file):
        nodes, edges = parse_graph_file(graph_file)
        super().__init__(nodes, edges)


def parse_graph_file(graph_file):
    NODES = 'nodes'
    EDGES = 'edges'

    with open(graph_file) as f:
        lines = f.readlines()

    nodes = []
    edges = []
    reader_state = None
    for line in lines:
        if line.startswith(NODES) and reader_state is None:
            reader_state = NODES
        elif line.startswith(EDGES):
            reader_state = EDGES
        elif reader_state == NODES and line != '\n':
            nodes.append(Node(int(line[1:])))
        elif reader_state == EDGES and line != '\n':
            s = line.split('->')
            from_node_id = int(s[0].strip()[1:])
            to_node_id = int(s[1].strip()[1:])
            edges.append(Edge(from_node_id, to_node_id))
    return nodes, edges
