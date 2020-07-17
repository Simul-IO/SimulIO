import random
from abc import ABC, abstractmethod
from copy import deepcopy
from random import shuffle

from simpleeval import EvalWithCompoundTypes


class BaseSimulator(ABC):
    def __init__(self, graph, transactions):
        self.graph = graph
        self.transactions = transactions

        self.states = {
            node.id: {'alive': True} for node in self.graph.nodes
        }
        self.neighbours = {
            node.id: self._make_local_neighbours(node.id) for node in graph.nodes
        }
        self.send_queue = []
        self.init_states()

    def _make_local_neighbours(self, node_id):
        neighbours = set()
        for edge in self.graph.edges:
            if edge.from_id == node_id:
                neighbours.add(edge.to_id)
            elif edge.to_id == node_id:
                neighbours.add(edge.from_id)
        neighbours = list(neighbours)
        n = len(neighbours)
        shuffled_ids = list(range(n))
        shuffle(shuffled_ids)

        all_shuffled_neighbours = {}
        reversed_all_shuffled_neighbours = {}
        for i in range(n):
            all_shuffled_neighbours[shuffled_ids[i]] = neighbours[i]
            reversed_all_shuffled_neighbours[neighbours[i]] = shuffled_ids[i]

        send_shuffled_neighbours = {}
        reversed_receive_shuffled_neighbours = {}
        for edge in self.graph.edges:
            if edge.from_id == node_id:
                send_shuffled_neighbours[reversed_all_shuffled_neighbours[edge.to_id]] = edge.to_id
            elif edge.to_id == node_id:
                reversed_receive_shuffled_neighbours[edge.from_id] = reversed_all_shuffled_neighbours[edge.from_id]

        return {
            'all': all_shuffled_neighbours,
            'reversed': reversed_all_shuffled_neighbours,
            'send': send_shuffled_neighbours,
            'reversed_receive': reversed_receive_shuffled_neighbours,
        }

    def _get_initial_state(self, node_id):
        return {
            'send_neighbour_ids': list(self.neighbours[node_id]['send'].keys()),
            'receive_neighbour_ids': list(self.neighbours[node_id]['reversed_receive'].values()),
        }

    def _eval(self, code, args):
        return EvalWithCompoundTypes(names=args).eval(code)

    def _translate_node_id_to_local_id(self, node_id, message_node_id):
        return self.neighbours[node_id]['reversed_receive'][message_node_id]

    def _is_alive(self):
        for state in self.states.values():
            if state['alive']:
                return True
        return False

    def init_states(self):
        next_states = {}
        for node_id, current_state in self.states.items():
            if 'init' in self.transactions:
                next_state = self._eval(self.transactions['init'].effect, {
                    'current_state': current_state,
                    **self._get_initial_state(node_id),
                })
                state = deepcopy(current_state)
                state.update(next_state)
                self.states[node_id] = state
                self._push_messages(node_id, 'init')

    def _receive(self, from_node_id, to_node_id, message):
        current_state = self.states[to_node_id]
        from_local_id = self._translate_node_id_to_local_id(to_node_id, from_node_id)

        next_state = self._eval(self.transactions['receive'].effect, {
            'current_state': current_state,
            'from_node': from_local_id,
            'message': message,
        })
        self.states[to_node_id].update(next_state)
        self._push_messages(to_node_id, 'receive')

    def _push_messages(self, node_id, transaction_name):
        messages = self._eval(self.transactions[transaction_name].output, {
            'current_state': self.states[node_id],
        })

        for to_local_id, message in messages:
            to_node_id = self.neighbours[node_id]['send'][to_local_id]
            self.send_queue.append((node_id, to_node_id, message))

    def _run_transaction(self, node_id, transaction_name):
        state = self.states[node_id]
        transaction = self.transactions[transaction_name]
        is_satisfied = self._eval(transaction.pre_condition, {
            'current_state': state,
        })
        if not is_satisfied:
            return
        next_state = self._eval(transaction.effect, {
            'current_state': state,
        })
        self.states[node_id].update(next_state)
        self._push_messages(node_id, transaction_name)

    @abstractmethod
    def run(self):
        pass


class SyncSimulator(BaseSimulator):
    def __init__(self, graph, transactions):
        super().__init__(graph, transactions)

    def _receive_messages(self):
        messages = deepcopy(self.send_queue)
        self.send_queue.clear()
        for from_node_id, to_node_id, message in messages:
            self._receive(from_node_id, to_node_id, message)

    def run(self):
        round_number = 0
        while self._is_alive():
            print('ROUND', round_number)
            self._receive_messages()
            for node_id in self.states:
                for transaction_name in self.transactions:
                    if transaction_name in ['init', 'receive']:
                        continue
                    self._run_transaction(node_id, transaction_name)

            round_number += 1


class SyncSimulatorWithUID(SyncSimulator):
    def __init__(self, graph, transactions):
        uids = set()
        while len(uids) < len(graph.nodes):
            uids.add(random.randint(1, len(graph.nodes) ** 10))
        uids = list(uids)
        shuffle(uids)
        self.uids = {}
        for i, node in enumerate(graph.nodes):
            self.uids[node.id] = uids[i]

        super().__init__(graph, transactions)

    def _get_initial_state(self, node_id):
        return {
            'uid': self.uids[node_id],
            **super()._get_initial_state(node_id),
        }
