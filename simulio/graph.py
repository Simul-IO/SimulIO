import random


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


class KRegularRing(Graph):
    def __init__(self, n, k):
        nodes = []
        edges = []
        edges_set = set()
        for i in range(n):
            nodes.append(Node(i))
            for j in range(1, k + 1):
                edges_set.add((i, (i + j) % n))
                edges_set.add((i, (i + n - j) % n))
        for edge in edges_set:
            edges.append(Edge(edge[0], edge[1]))
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


class BipartiteGraph(Graph):
    def __init__(self, n, m):
        nodes = []
        edges = []
        for i in range(n + m):
            nodes.append(Node(i))
        for i in range(n):
            for j in range(n, n + m):
                edges.append(Edge(i, j))
                edges.append(Edge(j, i))
        super().__init__(nodes, edges)


class StarGraph(Graph):
    def __init__(self, n):
        nodes = []
        edges = []
        for i in range(n):
            nodes.append(Node(i))
            if i != 0:
                edges.append(Edge(0, i))
                edges.append(Edge(i, 0))

        super().__init__(nodes, edges)


class RandomGraph(Graph):
    def __init__(self, n, m):
        nodes = []
        edges = []
        for i in range(n):
            nodes.append(Node(i))
        edges_set = set()
        while len(edges_set) < 2 * m:
            random_index_1 = random.randint(0, n - 1)
            random_index_2 = random.randint(0, n - 1)
            if random_index_1 == random_index_2:
                continue
            edges_set.add((random_index_1, random_index_2))
            edges_set.add((random_index_2, random_index_1))
        for edge in edges_set:
            edges.append(Edge(edge[0], edge[1]))
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
            s = line.split(' ')
            if len(s) > 1 and s[1].startswith('Byz'):
                properties = {'byzantine': int(s[1][3:])}
                nodes.append(Node(int(s[0][1:]), properties))
            else:
                nodes.append(Node(int(line[1:])))
        elif reader_state == EDGES and line != '\n':
            s = line.split('->')
            from_node_id = int(s[0].strip()[1:])
            to_node_id = int(s[1].strip()[1:])
            edges.append(Edge(from_node_id, to_node_id))
    return nodes, edges
