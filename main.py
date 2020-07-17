import json

from simulio.graph import BidirectionalRing
from simulio.simulator import SyncSimulator, SyncSimulatorWithUID
from simulio.transaction import parse

if __name__ == '__main__':
    with open('./examples/leader_election_automata.py') as f:
        lines = f.readlines()
    ring10 = BidirectionalRing(10)
    simulator = SyncSimulatorWithUID(ring10, parse(lines))
    simulator.run()
    with open('result.json', 'w') as f:
        json.dump({
            'graph': simulator.graph.to_dict(),
            'steps': simulator.details,
        }, f)
