# MAS. Activity 2 — Coordinated Cleaning Robots

## Project Description

This project simulates a multi-agent cleaning system using Python and the Mesa framework, and compares two kinds of robots:

- **Max-Plus robots (coordinated):** they know where the dirty cells are and coordinate their actions through a **Coordination Graph + Max-Plus message passing**.
- **Random robots (Activity M1):** if their current cell is dirty they clean it; otherwise they try to move to one of the eight neighboring cells at random. They do not communicate.

The simulation takes place in a 30 × 20 room (600 cells) with 100 randomly placed dirty cells. It ends when every cell is clean or when the maximum of 500 steps is reached. The goal is to measure, for teams of 1, 2, 4, 8 and 16 robots, the probability of cleaning the whole room within 500 steps, the mean cleaning time and the mean number of movements.

## How the Coordination Works

1. **Coordination graph.** Two robots are connected when their Manhattan distance is at most `D = 5`. The graph is rebuilt every step.
2. **Actions.** A robot standing on a dirty cell stays and cleans it. Otherwise it can:
   - **a:** take one step toward one of its `K = 3` nearest dirty cells,
   - **b:** stay in place,
   - **c:** move to a random clean neighboring cell.
3. **Local utility.** Moving toward a dirty cell gives `A = 10` (minus `LAMBDA = 1` per extra cell of distance compared with the nearest one), staying gives `B = 0`, and any other move gives `C = -1`.
4. **Pairwise payoffs between neighbors.** `V = -20` if both robots head to the same dirty cell or move into the same cell; `W = -20` if a robot moves into the cell where its neighbor stays (for example, while cleaning); `U = 5` if both move to different cells; `Z = 0` otherwise.
5. **Max-Plus.** Robots exchange normalized messages for up to 50 iterations (or until they converge), then each robot picks the action with the best local utility plus incoming messages.

When the module is loaded, `Coordination.py` checks that the parameters make two robots that want the same dirty cell split up instead of following each other (`V < C + U - A` and `W < C + U - A`).

## Dependencies

- Python 3.11
- Mesa 3.x
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebook

## Project Files

- `Agent.py`: Defines `RobotAgent` (executes the action chosen by Max-Plus) and `RandomRobotAgent` (the random robot from M1).
- `Coordination.py`: Parameters, coordination graph, possible actions, utilities, pairwise payoffs and the Max-Plus algorithm.
- `Model.py`: Manages the room, dirty cells, robots and simulation statistics. Supports `agentType="maxplus"` or `"random"`, and an optional `startAtOrigin` mode where every robot starts at cell [1,1].
- `Test.py`: Runs 100 simulations (seeds 0–99) for each method and team size and saves them to `test_results.csv`.
- `View.py`: Animated visualization of one simulation with a Pause / Play button.
- `Analysis.ipynb`: Experimental analysis, graphs, the effect of coordination on congestion, and conclusions.
- `test_results.csv`: Results of the 1,000 simulations (one row per simulation).

## How to Run

To visualize the simulation:

```
python3 View.py
```

You can change the team size, robot type and starting mode with the constants at the top of `View.py` (`NUM_AGENTS`, `AGENT_TYPE`, `START_AT_ORIGIN`).

To execute the experiments:

```
python3 Test.py
```

To review the analysis, open `Analysis.ipynb` in Jupyter Notebook or VS Code and execute the cells.

## Results Summary

Averages over 100 simulations per configuration (30 × 20 room, 100 dirty cells, 500 steps maximum).

| Method | Robots | Success probability | Avg. steps | Avg. cleaned (%) | Avg. total moves |
|---|---|---|---|---|---|
| Max-Plus | 1 | 1.00 | 277.61 | 100.00 | 277.61 |
| Max-Plus | 2 | 1.00 | 153.99 | 100.00 | 307.98 |
| Max-Plus | 4 | 1.00 | 90.31 | 100.00 | 361.23 |
| Max-Plus | 8 | 1.00 | 53.12 | 100.00 | 424.94 |
| Max-Plus | 16 | 1.00 | 31.29 | 100.00 | 500.64 |
| Random (M1) | 1 | 0.00 | 500.00 | 29.40 | 441.29 |
| Random (M1) | 2 | 0.00 | 500.00 | 50.17 | 892.85 |
| Random (M1) | 4 | 0.00 | 500.00 | 74.94 | 1,810.84 |
| Random (M1) | 8 | 0.03 | 498.58 | 93.25 | 3,658.83 |
| Random (M1) | 16 | 0.60 | 423.48 | 99.32 | 6,261.76 |

Main findings:

- The Max-Plus robots cleaned the whole room in every simulation; the random robots reached at most a 0.60 success probability (16 robots).
- Sixteen Max-Plus robots were 8.87 times faster than one, so the speedup is not proportional to team size. Based on extra movements per step saved, eight robots are a good balance between speed and movements in this room.
- Compared with the same robots without the coordination graph, message passing reduced shared-cell events and also shortened cleaning time (for example, 90.31 vs. 105.93 steps with four robots).

## Authors

* Adriana Sandoval Santos - A01667445
* Marbella Barba De los Santos - A01660946
* Javier Padilla Marcial - A01660945
* Camila Quintanilla Cabrera - A01662397
* Alani Daniel Garcia Maya - A01277308

## Repository

https://github.com/Adrisandoval2006/MAS.-Activity-2
