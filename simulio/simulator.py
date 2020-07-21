import random
from abc import ABC, abstractmethod
from copy import deepcopy
from random import shuffle

from simulio.executor import simple_exec
from simulio.memory_usage_calculator import get_memory_size

PREDEFINED_TRANSITIONS = ['init', 'receive', 'visualize']


class BaseSimulator(ABC):
    def __init__(self, graph, main_transitions, byzantine_transitions, link_failure_prob):
        self.graph = graph
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
        self.total_messages = 0
        self.total_send_messages_by_node = {
            node.id: 0 for node in self.graph.nodes
        }
        self.total_received_messages_by_node = {
            node.id: 0 for node in self.graph.nodes
        }
        self.max_memory_by_node = {
            node.id: 0 for node in self.graph.nodes
        }
        self.details = []
        self.link_failure_prob = float(link_failure_prob)  # The probability that each message can be lost

        self.transitions = self._initialize_transitions(main_transitions, byzantine_transitions)
        self.init_states()

    def _add_to_details(self, active_nodes=None, with_messages=True):
        self.details.append({
            'send_messages': deepcopy(self.send_queue) if with_messages else [],
            'total_messages': self.total_messages,
            'states': {
                node_id: {
                    'borderColor': '#ad8b0e' if active_nodes is None or node_id in active_nodes else '#cccccc',
                    **self._exec(self.transitions[node_id]['visualize'].effect, {
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

    def _initialize_transitions(self, main_transitions, byzantine_transitions):
        node_transitions = {}
        for node in self.graph.nodes:
            if 'byzantine' in node.properties:
                node_transitions[node.id] = byzantine_transitions[node.properties['byzantine'] - 1]
            else:
                node_transitions[node.id] = main_transitions
        return node_transitions

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
            transitions = self.transitions[node_id]
            if 'init' in transitions:
                next_state = self._exec(transitions['init'].effect, {
                    'state': current_state,
                    **self._get_initial_state(node_id),
                })
                state = deepcopy(current_state)
                state.update(next_state)
                self.states[node_id] = state
                self._push_messages(node_id, 'init')
                self.max_memory_by_node[node_id] = max(get_memory_size(self.states[node_id]),
                                                       self.max_memory_by_node[node_id])

    def _receive(self, from_node_id, to_node_id, message):
        current_state = self.states[to_node_id]
        from_local_id = self._translate_node_id_to_local_id(to_node_id, from_node_id)
        transitions = self.transitions[to_node_id]

        next_state = self._exec(transitions['receive'].effect, {
            'state': current_state,
            'from_node': deepcopy(from_local_id),
            'message': message,
        })
        self.states[to_node_id].update(next_state)
        self.total_received_messages_by_node[to_node_id] += 1
        self._push_messages(to_node_id, 'receive')
        self.max_memory_by_node[to_node_id] = max(get_memory_size(self.states[to_node_id]),
                                                  self.max_memory_by_node[to_node_id])

    def _push_messages(self, node_id, transition_name):
        changed = False
        transition = self.transitions[node_id][transition_name]

        messages = self._exec(transition.output, {
            'state': self.states[node_id],
        })

        for to_local_id, message in messages:
            if random.random() < self.link_failure_prob:
                continue
            changed = True
            to_node_id = self.neighbours[node_id]['send'][to_local_id]
            self.send_queue.append((node_id, to_node_id, message))
            self.total_messages += 1
            self.total_send_messages_by_node[node_id] += 1
        return changed

    def _run_transition(self, node_id, transition_name):
        state = self.states[node_id]
        transition = self.transitions[node_id][transition_name]

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
        self.max_memory_by_node[node_id] = max(get_memory_size(self.states[node_id]),
                                               self.max_memory_by_node[node_id])
        if self._push_messages(node_id, transition_name):
            changed = True
        return changed

    def _get_mean_messages_per_node(self):
        sum_send_msg = 0
        sum_recv_msg = 0
        for node_id in self.states:
            sum_send_msg += self.total_send_messages_by_node[node_id]
            sum_recv_msg += self.total_received_messages_by_node[node_id]
        mean_send = sum_send_msg / len(self.graph.nodes)
        mean_recv = sum_recv_msg / len(self.graph.nodes)
        return mean_send, mean_recv

    def _get_max_memory_used_by_node(self):
        max_used = 0
        for node_id in self.states:
            if self.max_memory_by_node[node_id] > max_used:
                max_used = self.max_memory_by_node[node_id]
        return max_used

    @abstractmethod
    def run(self):
        pass


class RandomUIDSimulator(BaseSimulator, ABC):
    def __init__(self, graph, main_transitions, byzantine_transitions, link_failure_prob):
        uids = set()
        while len(uids) < len(graph.nodes):
            uids.add(random.randint(1, len(graph.nodes) ** 2))
        uids = list(uids)
        shuffle(uids)
        self.uids = {}
        for i, node in enumerate(graph.nodes):
            self.uids[node.id] = uids[i]

        BaseSimulator.__init__(self, graph, main_transitions, byzantine_transitions, link_failure_prob)

    def _get_initial_state(self, node_id):
        return {
            'uid': self.uids[node_id],
            **super()._get_initial_state(node_id),
        }


class SyncSimulator(BaseSimulator):
    def __init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob):
        self.limit_steps = limit_steps
        BaseSimulator.__init__(self, graph, main_transitions, byzantine_transitions, link_failure_prob)

    def _receive_messages(self, active_nodes):
        messages = deepcopy(self.send_queue)
        self.send_queue.clear()
        for from_node_id, to_node_id, message in messages:
            self._receive(from_node_id, to_node_id, message)
            active_nodes.add(to_node_id)

    def run(self):
        self._add_to_details(with_messages=False)
        self._add_to_details(with_messages=True)
        round_number = 0
        while self._is_alive():
            if self.limit_steps is not None and round_number >= self.limit_steps:
                break
            active_nodes = set()
            self._receive_messages(active_nodes)
            for node_id in self.states:
                has_active_transaction = True
                while has_active_transaction:
                    has_active_transaction = False
                    if not self.states[node_id]['alive']:
                        continue
                    for transition_name in self.transitions[node_id]:
                        if transition_name in PREDEFINED_TRANSITIONS:
                            continue
                        if self._run_transition(node_id, transition_name):
                            has_active_transaction = True
                            active_nodes.add(node_id)
            self._add_to_details(active_nodes, with_messages=False)
            self._add_to_details(active_nodes, with_messages=True)
            round_number += 1

        mean_send_messages, mean_received_messages = self._get_mean_messages_per_node()
        print("Rounds: ", round_number)
        print("Total Messages: ", self.total_messages)
        print("Mean Send Messages: ", mean_send_messages)
        print("Mean Recv Messages: ", mean_received_messages)
        print("Max Memory Used By node: ", self._get_max_memory_used_by_node())


class SyncSimulatorWithRandomUID(SyncSimulator, RandomUIDSimulator):
    def __init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob):
        RandomUIDSimulator.__init__(self, graph, main_transitions, byzantine_transitions, link_failure_prob)
        SyncSimulator.__init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob)


class AsyncSimulator(BaseSimulator):
    def __init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob):
        self.limit_steps = limit_steps
        BaseSimulator.__init__(self, graph, main_transitions, byzantine_transitions, link_failure_prob)

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

    def _get_phase(self):
        max_phase = 0
        for node_id in self.states:
            if self.states[node_id]['phase'] > max_phase:
                max_phase = self.states[node_id]['phase']
        return max_phase

    def run(self):
        self._add_to_details()
        steps = 0
        while self._is_alive():
            if self.limit_steps is not None and steps >= self.limit_steps:
                break
            active_nodes = set()
            if self._receive_messages(active_nodes):
                self._add_to_details(active_nodes)
                steps += 1
                continue
            node_id = random.choice(list(self.states.keys()))
            if not self.states[node_id]['alive']:
                continue
            transition_name = random.choice(list(self.transitions[node_id].keys()))
            if transition_name in ['init', 'receive', 'visualize']:
                continue
            if self._run_transition(node_id, transition_name):
                active_nodes.add(node_id)
                self._add_to_details(active_nodes)
            steps += 1

        mean_send_messages, mean_received_messages = self._get_mean_messages_per_node()
        print("Phases: ", self._get_phase())
        print("Total Messages: ", self.total_messages)
        print("Mean Send Messages: ", mean_send_messages)
        print("Mean Recv Messages: ", mean_received_messages)
        print("Max Memory Used By node: ", self._get_max_memory_used_by_node())


class AsyncSimulatorWithRandomUID(AsyncSimulator, RandomUIDSimulator):
    def __init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob):
        RandomUIDSimulator.__init__(self, graph, main_transitions, byzantine_transitions, link_failure_prob)
        AsyncSimulator.__init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob)


class FIFOAsyncSimulator(AsyncSimulator):
    def __init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob):
        AsyncSimulator.__init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob)

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
    def __init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob):
        FIFOAsyncSimulator.__init__(self, graph, main_transitions, byzantine_transitions, limit_steps,
                                    link_failure_prob)


class OrderedAsyncSimulatorWithRandomUID(RandomUIDSimulator, FIFOAsyncSimulator):
    def __init__(self, graph, main_transitions, byzantine_transitions, limit_steps, link_failure_prob):
        RandomUIDSimulator.__init__(self, graph, main_transitions, byzantine_transitions, link_failure_prob)
        FIFOAsyncSimulator.__init__(self, graph, main_transitions, byzantine_transitions, limit_steps,
                                    link_failure_prob)
