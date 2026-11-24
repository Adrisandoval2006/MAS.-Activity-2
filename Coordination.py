"""
Implements coordination graphs and Max-Plus message passing for autonomous cleaning robots.
Authors: Adriana Sandoval Santos - A01667445
         Marbella Barba De los Santos - A01660946
         Javier Padilla Marcial - A01660945
         Camila Quintanilla Cabrera - A01662397
         Alani Daniel Garcia Maya - A01277308
Date: 2026-11-22
"""

# Parameters selected for coordination.
A = 10       # Reward for moving toward a dirty cell.
B = 0        # Utility for staying
C = -1       # Utility for moving to a clean cell
D = 5        # Maximum distance between neighbors
U = 5        # Reward for choosing different destinations
V = -10      # Penalty for choosing the same destination
W = 0        # Payoff in other cases

# Builds an undirected graph using Manhattan distance.
# Parameters: 
#   agents: List of robots in the simulation.
# Returns: Dictionary mapping robot IDs to neighboring robot IDs.
def buildCoordinationGraph(agents):

    graph = {}

    for agent in agents:
        graph[agent.unique_id] = []

    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):

            robot1 = agents[i]
            robot2 = agents[j]

            distance = manhattan(robot1.pos, robot2.pos)

            if distance <= D:
                graph[robot1.unique_id].append(robot2.unique_id)
                graph[robot2.unique_id].append(robot1.unique_id)
                
    return graph

# Calculates Manhattan distance between two positions.
# Parameters: 
#   position: Initial coordinates.
#   destCell: Destination coordinates.
# Returns: Manhattan distance between both positions.
def manhattan(position, destCell):
    return abs(position[0] - destCell[0]) + abs(position[1] - destCell[1])

# Selects a valid neighboring cell toward the target.
# Parameters: 
#   agent: Robot selecting its movement.
#   target: Dirty cell selected as the target.
#   model: Simulation model containing the grid.
# Returns: Position that reduces distance to the target.
def goToward(agent, target, model):
    if agent.pos == target:
        return agent.pos
    getMyNeighbors = model.grid.get_neighborhood(agent.pos, moore=False, include_center=False)
    bestDistance = min(manhattan(cell, target) for cell in getMyNeighbors)
    bestCells = [cell for cell in getMyNeighbors if manhattan(cell, target) == bestDistance]
    return model.random.choice(sorted(bestCells))

# Generates possible actions for one robot.
# Parameters: 
#   agent: Robot whose actions are evaluated.
#   model: Simulation model containing dirty cells and grid.
# Returns: List of actions with type and destination.
def getPossibleActions(agent, model):
    actions = []
    getMyNeighbors = model.grid.get_neighborhood(agent.pos, moore=False, include_center = False)
    
    dirtyStep = None

    if model.dirtyCells:
        dirtyTarget = min(
            model.dirtyCells,
            key=lambda cell: (manhattan(agent.pos, cell), cell)
            )
        
        dirtyStep = goToward(agent, dirtyTarget, model)
        
        actions.append({
            "type": "a",
            "destination": dirtyStep
        })

    # Action b: stay in the current cell
    actions.append({
        "type": "b",
        "destination": agent.pos
    })

    # Action c: move to the nearest clean cell
    cleanCells = [
        cell for cell in getMyNeighbors
        if cell not in model.dirtyCells and cell != dirtyStep
    ]

    if cleanCells:
        actions.append({
            "type": "c",
            "destination": model.random.choice(sorted(cleanCells))
        })

    return actions

# Calculates the local utility of an action.
# Parameters: 
#   action: Action containing its type and destination.
# Returns: Numeric utility assigned to the action.
def calculateLocalUtility(action):

    if action["type"] == "a":
        return A

    if action["type"] == "b":
        return B

    return C

# Calculates the payoff between two coordinated actions.
# Parameters: action1: First robot's action.
# action2: Second robot's action.
# Returns: Reward, penalty, or neutral payoff.
def calculateNeighborPayoff(action1, action2):

    if action1["type"] != "b" and action2["type"] != "b":
        if action1["destination"] == action2["destination"]:
            return V

        return U

    return W

# Runs Max-Plus message passing to coordinate robot actions.
# Parameters: 
#   agents: Robots participating in coordination.
#   graph: Dictionary representing the coordination graph.
#   model: Simulation model containing the environment.
#   iterations: Maximum number of message-passing iterations.
#   tolerance: Minimum change required to continue iterations.
# Returns: Dictionary mapping each robot ID to its selected action.
def maxPlus(agents, graph, model, iterations=50, tolerance=0.0001):
    actions = {}

    for agent in agents:
        actions[agent.unique_id] = getPossibleActions(agent, model)

    messages = {}

    for robot in graph:
        for neighbor in graph[robot]:
            messages[(robot, neighbor)] = [
                0.0 for _ in actions[neighbor]
            ]

    iteration = 0
    converged = False

    # Update all messages synchronously until convergence.
    while iteration < iterations and not converged:
        newMessages = {}

        for robot in graph:
            for neighbor in graph[robot]:
                message = []

                for neighborAction in actions[neighbor]:
                    bestValue = float("-inf")

                    for i, robotAction in enumerate(actions[robot]):
                        value = calculateLocalUtility(robotAction)

                        for otherRobot in graph[robot]:
                            if otherRobot != neighbor:
                                value += messages[(otherRobot, robot)][i]

                        value += calculateNeighborPayoff(robotAction,neighborAction)

                        bestValue = max(bestValue, value)

                    message.append(bestValue)

                maxValue = max(message)

                normalizedMessage = [value - maxValue for value in message]

                newMessages[(robot, neighbor)] = normalizedMessage

        maxDifference = 0.0

        for key in messages:
            for oldValue, newValue in zip(messages[key], newMessages[key]):
                difference = abs(newValue - oldValue)
                maxDifference = max(maxDifference, difference)

        messages = newMessages
        converged = maxDifference < tolerance
        iteration += 1

    selectedActions = {}

    # Select each robot's action from its final local belief.
    for robot in graph:
        bestValue = float("-inf")
        bestAction = actions[robot][0]

        for i, action in enumerate(actions[robot]):
            value = calculateLocalUtility(action)

            for neighbor in graph[robot]:
                value += messages[(neighbor, robot)][i]

            if value > bestValue:
                bestValue = value
                bestAction = action

        selectedActions[robot] = bestAction

    return selectedActions
