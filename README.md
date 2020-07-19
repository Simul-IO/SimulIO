# SimulIO
SimulIO is a timed I/O automata simulator for distributed algorithms written in python 3 and support custom topology
 and graphs.

## Installation and usage
Follow below instructions.
1. Create a virtualenv using `python3 -m venv env` and active it using `source env/bin/activate`.
2. Install dependencies using `pip3 install -r requirements.txt`
3. Now you can run it with `./simulate` file. for example with:
```bash
python3 simulate -a examples/automata/leader_election_automata.ioa -g UnidirectionalRing -n 10 -t SyncSimulatorWithUID -o result.json
```
4. Now, you can open [`Visualizer/index.html`](https://simul-io.github.io/SimulIO/Visualizer/) using web browser and 
drag and drop `result.json` to see visualization. (use left/right arrow keys to see prev/next steps.)

