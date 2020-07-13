from typing import List

from simulio.automaton.state import State
from simulio.automaton.transaction import Transaction


class TIOAutomaton:
    def __init__(self, state: State, transactions: List[Transaction]):
        self.state = state
        self.transactions = transaction
