from typing import Type

from simulio.automaton import TIOAutomaton
from simulio.topology import Topology


class SimulatedResult:
    pass


def simulate(topology: Topology, automaton: Type[TIOAutomaton], state_generator) -> SimulatedResult:
    pass
