# SimulIO: Timed I/O Automata simulator
SimulIO is a timed I/O automata simulator for distributed algorithms written in python3 and supports custom topology and graphs.

The reason we intend to develop a new simulator is that the existing simulators have no active development and use deprecated libraries and some are not open source and not well-documented. Also, we needed to simulate algorithms under specific circumstances in our course project, that existing simulators didn't support them, so we developed SimulIO.

The SimulIO includes, but is not limited to, the following features:
- Handle Simulating both Synchronous and Asynchronous Systems
- Handle nodes run different algorithms
- Handle Node-Failure (Byzantine or Stopping-Failure) and Link-Failure
- Graph and Run Visualization
- Flexible for custom networks and algorithms 
 
 ## Installation and usage  
Follow the below instructions.  
1. Clone the project.
2. Create a virtualenv using `python3 -m venv env` and active it using `source env/bin/activate`.  
3. Install dependencies using `pip3 install -r requirements.txt`  
4. Now you can run it with `./simulate` file. for example with:  
```bash  
./simulate -a examples/automata/leader_election_automata.ioa -g unidirectional-ring 10 -r -t sync -o result.json
```
5. Now, you can open [`Visualizer/index.html`](https://simul-io.github.io/SimulIO/Visualizer/) using a web browser and drag and drop `result.json` to see the visualization. (use Left/Right arrow keys to see previous/next steps.)

## Design Structure
For simulating, we have three main components:
### Graph
Specify the network, vertices as nodes and edges as communication links. In SimulIO, can specify some nodes as special nodes (Byzantine nodes) each can run different algorithms, also every link can have its own properties and so many situations like stopping-failure, byzantine-failure and link-failure can be simulated. 
###  Automata
Automata is a list of transitions. Every transition has four parts:
1. **Transition Name**, it is a unique string.
2. **Precondition**, it is a function that gets current state as an argument and returns `True` or `False`. It can't change the state.
3. **Effect**, it is a function that gets  current state and returns new state. 
4. **Output**, this function can return a list of tuples `(id, message)` that means send `message` to neighbor with `uid=id`. 

**Effect** and **Output** are optional, no **Output** means send no messages to neighbors and no **Effect** means state will not change.
 
There are two required transitions: **init** and **receive** that has no **Precondition**. **init** transition specifies the initial state of node and only returns a dictionary. For example the UID of node or node neighbor IDs provided in **init** transition. 

### Simulator
Simulator is responsible for running defined Automata on given Graph. Has different methods to run: Synchronous or Asynchronous, messages received in FIFO channel mode or arbitrary mode, Deterministic or Probabilistic mode (let use random functions in Automata definition or not) and etc.
Simulator consider a virtual machine per node that every machine has its own state and neighbors (a dictionary that hold relation between local neighbors and real nodes). Then simulator call **Effect** function of  **init** transition with a list of node neighbors as input (for algorithms that nodes know the entire network, input can be all graph information and not just the neighbor IDs) on every node and the returning dictionary will be the new state of node. Then call the **Output** function and add its return value to central send queue. After **init** transition done for all nodes, the **receive** transition or transitions that their **Precondition** is satisfied will run based on simulating conditions (Synchronous or Asynchronous or etc).

