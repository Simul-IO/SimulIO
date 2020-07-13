from abc import ABC
from typing import List, Callable

from simulio.automaton import TIOAutomaton, State
from simulio.topology.graph import Graph


class Topology(ABC):
    def __init__(self, graph: Graph, automaton: TIOAutomaton, initial_state: Callable[[]: State]):
        self.graph = graph
        self.automaton = automaton
        self.initial_state = initial_state
