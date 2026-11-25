"""
Coordination graph and Max-Plus message passing for the cleaning robots.
Authors: Adriana Sandoval Santos - A01667445
         Marbella Barba De los Santos - A01660946
         Javier Padilla Marcial - A01660945
         Camila Quintanilla Cabrera - A01662397
         Alani Daniel Garcia Maya - A01277308
Date: 2026-11-21
"""

# Parameters selected
A = 10       # Utility for moving to a dirty cell
B = 0        # Utility for staying
C = -1       # Utility for moving to a clean cell
D = 5        # Maximum distance between neighbors
U = 5        # Reward for choosing different destinations
V = -10      # Penalty for choosing the same destination
W = 0        # Payoff in other cases


# Builds the coordination graph: two robots are neighbors when their
# Manhattan distance is at most D.
# Parameters: agents: List of robots.
# Returns: Dictionary mapping each robot id to its list of neighbor ids.
def buildCoordinationGraph(agents):

    graph = {}

    for agent in agents:
        graph[agent.unique_id] = []

    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):

            robot1 = agents[i]
            robot2 = agents[j]

            x1, y1 = robot1.pos
            x2, y2 = robot2.pos

            distance = abs(x1 - x2) + abs(y1 - y2)

            if distance <= D:
                graph[robot1.unique_id].append(robot2.unique_id)
                graph[robot2.unique_id].append(robot1.unique_id)

    return graph


# Calculates the Manhattan distance between two cells.
# Parameters: position: First cell; destCell: Second cell.
# Returns: Integer distance.
def manhattan(position, destCell):
    return abs(position[0] - destCell[0]) + abs(position[1] - destCell[1])


# Chooses the 4-neighbor cell that gets the robot closest to a target.
# Ties are broken at random among the closest cells.
# Parameters: agent: Robot; target: Target cell; model: Simulation model.
# Returns: The chosen neighbor cell.
def goToward(agent, target, model):
    getMyNeighbors = model.grid.get_neighborhood(
        agent.pos, moore=False, include_center=False
    )
    bestDistance = min(manhattan(cell, target) for cell in getMyNeighbors)
    best = [
        cell for cell in getMyNeighbors
        if manhattan(cell, target) == bestDistance
    ]
    return model.random.choice(sorted(best))


# Lists the actions available to a robot in the current step.
# Parameters: agent: Robot; model: Simulation model.
# Returns: List of actions, each a dictionary with "type" and "destination".
def getPossibleActions(agent, model):
    actions = []
    getMyNeighbors = model.grid.get_neighborhood(
        agent.pos, moore=False, include_center=False
    )

    # Action a: one step toward the nearest dirty cell
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

    # Action c: move to a random clean neighbor (different from action a)
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


# Local utility q_i of one action.
# Parameters: action: Action dictionary.
# Returns: A, B or C depending on the action type.
def calculateLocalUtility(action):

    if action["type"] == "a":
        return A

    if action["type"] == "b":
        return B

    return C


# Pairwise payoff f_ij between the actions of two neighbor robots.
# Parameters: action1, action2: Actions of the two robots.
# Returns: V if both move to the same cell, U if both move to different
# cells, and W if at least one of them stays.
def calculateNeighborPayoff(action1, action2):

    if action1["type"] != "b" and action2["type"] != "b":

        if action1["destination"] == action2["destination"]:
            return V

        return U

    return W


# Runs Max-Plus message passing over the coordination graph.
# Parameters: agents: List of robots; graph: Coordination graph;
# model: Simulation model; iterations: Maximum number of iterations;
# tolerance: Stops when no message changes more than this value.
# Returns: Dictionary mapping each robot id to its selected action.
def maxPlus(agents, graph, model, iterations=50, tolerance=0.0001):
    actions = {}

    for agent in agents:
        actions[agent.unique_id] = getPossibleActions(agent, model)

    # messages[(i, j)][k]: message from robot i to robot j about
    # robot j's k-th action. All messages start at zero.
    messages = {}

    for robot in graph:
        for neighbor in graph[robot]:

            messages[(robot, neighbor)] = [
                0.0 for _ in actions[neighbor]
            ]

    # Initializes the iteration and convergence variables.
    iteration = 0
    converged = False

    while iteration < iterations and not converged:
        newMessages = {}

        for robot in graph:
            for neighbor in graph[robot]:
                message = []

                for neighborAction in actions[neighbor]:
                    bestValue = float("-inf")
                    for i, robotAction in enumerate(actions[robot]):
                        value = calculateLocalUtility(robotAction)

                        # Adds what the other neighbors said about this action.
                        for otherRobot in graph[robot]:
                            if otherRobot != neighbor:
                                value += messages[(otherRobot, robot)][i]

                        value += calculateNeighborPayoff(
                            robotAction, neighborAction
                        )

                        bestValue = max(bestValue, value)

                    message.append(bestValue)

                # Normalizes the message so its maximum is 0.
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

    # Each robot picks the action with the best local utility plus
    # incoming messages.
    theSelectedActions = {}

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

        theSelectedActions[robot] = bestAction

    return theSelectedActions

