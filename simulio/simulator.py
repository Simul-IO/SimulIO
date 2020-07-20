import random
from abc import ABC, abstractmethod
from copy import deepcopy
from random import shuffle

from simulio.executor import simple_exec

PREDEFINED_TRANSITIONS = ['init', 'receive', 'visualize']


class BaseSimulator(ABC):
    def __init__(self, graph, transitions):
        self.graph = graph
        self.transitions = transitions

        self.states = {
            node.id: {
                'id': node.id,
                'alive': True,
            } for node in self.graph.nodes
        }
        self.neighbours = {
            node.id: self._make_local_neighbours(node.id) for node in graph.nodes
        }
        self.send_queue = []
        self.details = []
        self.init_states()

    def _add_to_details(self, active_nodes=None):
        self.details.append({
            'send_messages': deepcopy(self.send_queue),
            'states': {
                node_id: {
                    'borderColor': '#ad8b0e' if active_nodes is None or node_id in active_nodes else '#cccccc',
                    **self._exec(self.transitions['visualize'].effect, {
                        'state': state,
                    })} for node_id, state in self.states.items()
            }
        })

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
            'network_size': len(self.graph.nodes),
            'output_neighbour_ids': list(self.neighbours[node_id]['send'].keys()),
            'input_neighbour_ids': list(self.neighbours[node_id]['reversed_receive'].values()),
        }

    def _exec(self, code, args):
        return simple_exec(code, names=args)

    def _translate_node_id_to_local_id(self, node_id, message_node_id):
        return self.neighbours[node_id]['reversed_receive'][message_node_id]

    def _is_alive(self):
        for state in self.states.values():
            if state['alive']:
                return True
        return False

    def init_states(self):
        for node_id, current_state in self.states.items():
            if 'init' in self.transitions:
                next_state = self._exec(self.transitions['init'].effect, {
                    'state': current_state,
                    **self._get_initial_state(node_id),
                })
                state = deepcopy(current_state)
                state.update(next_state)
                self.states[node_id] = state
                self._push_messages(node_id, 'init')

    def _receive(self, from_node_id, to_node_id, message):
        current_state = self.states[to_node_id]
        from_local_id = self._translate_node_id_to_local_id(to_node_id, from_node_id)

        next_state = self._exec(self.transitions['receive'].effect, {
            'state': current_state,
            'from_node': from_local_id,
            'message': message,
        })
        self.states[to_node_id].update(next_state)
        self._push_messages(to_node_id, 'receive')

    def _push_messages(self, node_id, transition_name):
        changed = False
        messages = self._exec(self.transitions[transition_name].output, {
            'state': self.states[node_id],
        })

        for to_local_id, message in messages:
            changed = True
            to_node_id = self.neighbours[node_id]['send'][to_local_id]
            self.send_queue.append((node_id, to_node_id, message))
        return changed

    def _run_transition(self, node_id, transition_name):
        state = self.states[node_id]
        transition = self.transitions[transition_name]
        is_satisfied = self._exec(transition.pre_condition, {
            'state': state,
        })
        if not is_satisfied:
            return False
        changed = False
        next_state = self._exec(transition.effect, {
            'state': state,
        })
        if next_state:
            changed = True
        self.states[node_id].update(next_state)
        if self._push_messages(node_id, transition_name):
            changed = True
        return changed

    @abstractmethod
    def run(self):
        pass


class RandomUIDSimulator(BaseSimulator, ABC):
    def __init__(self, graph, transitions):
        uids = set()
        while len(uids) < len(graph.nodes):
            uids.add(random.randint(1, len(graph.nodes) ** 2))
        uids = list(uids)
        shuffle(uids)
        self.uids = {}
        for i, node in enumerate(graph.nodes):
            self.uids[node.id] = uids[i]

        super().__init__(graph, transitions)

    def _get_initial_state(self, node_id):
        return {
            'uid': self.uids[node_id],
            **super()._get_initial_state(node_id),
        }


class SyncSimulator(BaseSimulator):
    def __init__(self, graph, transitions):
        super().__init__(graph, transitions)

    def _receive_messages(self, active_nodes):
        messages = deepcopy(self.send_queue)
        self.send_queue.clear()
        for from_node_id, to_node_id, message in messages:
            self._receive(from_node_id, to_node_id, message)
            active_nodes.add(to_node_id)

    def run(self):
        self._add_to_details()
        round_number = 0
        while self._is_alive():
            active_nodes = set()
            self._receive_messages(active_nodes)
            for node_id in self.states:
                if not self.states[node_id]['alive']:
                    continue
                for transition_name in self.transitions:
                    if transition_name in PREDEFINED_TRANSITIONS:
                        continue
                    if self._run_transition(node_id, transition_name):
                        active_nodes.add(node_id)
            self._add_to_details(active_nodes)
            round_number += 1


class SyncSimulatorWithRandomUID(SyncSimulator, RandomUIDSimulator):
    def __init__(self, graph, transitions):
        super().__init__(graph, transitions)


class AsyncSimulator(BaseSimulator):
    def __init__(self, graph, transitions):
        super().__init__(graph, transitions)

    def _receive_index(self, index, active_nodes):
        new_messages = []
        new_messages.extend(self.send_queue[:index])
        new_messages.extend(self.send_queue[index + 1:])

        self._receive(*self.send_queue[index])
        active_nodes.add(self.send_queue[index][1])
        self.send_queue = new_messages

    def _receive_messages(self, active_nodes):
        if len(self.send_queue) > 0 and random.randint(0, len(self.graph.nodes)) == 0:
            self._receive_index(random.randint(0, len(self.send_queue) - 1), active_nodes)
            return True
        return False

    def run(self):
        self._add_to_details()
        while self._is_alive():
            active_nodes = set()
            if self._receive_messages(active_nodes):
                self._add_to_details(active_nodes)
                continue
            node_id = random.choice(list(self.states.keys()))
            if not self.states[node_id]['alive']:
                continue
            transition_name = random.choice(list(self.transitions.keys()))
            if transition_name in ['init', 'receive', 'visualize']:
                continue
            if self._run_transition(node_id, transition_name):
                active_nodes.add(node_id)
                self._add_to_details(active_nodes)


class AsyncSimulatorWithRandomUID(AsyncSimulator, RandomUIDSimulator):
    def __init__(self, graph, transitions):
        super().__init__(graph, transitions)


class FIFOAsyncSimulator(AsyncSimulator):
    def __init__(self, graph, transitions):
        super().__init__(graph, transitions)

    def _receive_messages(self, active_nodes):
        if len(self.send_queue) > 0 and random.randint(0, len(self.graph.nodes)) == 0:
            random_node = random.choice(self.graph.nodes).id
            random_index = None
            for i, (from_node_id, to_node_id, message) in enumerate(self.send_queue):
                if to_node_id == random_node:
                    random_index = i
                    break

            if random_index is None:
                return False

            self._receive_index(random_index, active_nodes)
            return True
        return False


class OrderedAsyncSimulator(FIFOAsyncSimulator):
    def __init__(self, graph, transitions):
        super().__init__(graph, transitions)


class OrderedAsyncSimulatorWithRandomUID(RandomUIDSimulator, FIFOAsyncSimulator):
    def __init__(self, graph, transitions):
        super().__init__(graph, transitions)
