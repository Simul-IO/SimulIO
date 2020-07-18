import json

from simulio.graph import UnidirectionalRing, CompleteGraph
from simulio.simulator import SyncSimulator, SyncSimulatorWithUID, AsyncSimulatorWithUID
from simulio.transaction import parse

if __name__ == '__main__':
    with open('./examples/leader_election_automata.py') as f:
        lines = f.readlines()
    ring10 = UnidirectionalRing(10)
    simulator = AsyncSimulatorWithUID(ring10, parse(lines))
    simulator.run()
    with open('result.json', 'w') as f:
        json.dump({
            'graph': simulator.graph.to_dict(),
            'steps': simulator.details,
        }, f)
