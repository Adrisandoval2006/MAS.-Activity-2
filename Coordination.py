# Parameters selected
A = 10       # Utility for moving to a dirty cell
B = 0        # Utility for staying
C = -1       # Utility for moving to a clean cell
D = 5        # Maximum distance between neighbors
U = 5        # Reward for choosing different destinations
V = -10      # Penalty for choosing the same destination
W = 0        # Payoff in other cases

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

def manhattan(position, destCell):
    return abs(position[0] - destCell[0]) + abs(position[1] - destCell[1])

def goToward(agent, target, model):
    getMyNeighbors = model.grid.get_neighborhood(agent.pos, moore=False, include_center = False)
    bestDistance = min(manhattan(cell, target) for cell in getMyNeighbors)
    best = [cell for cell in getMyNeighbors if manhattan(cell, target) == bestDistance]
    return model.random.choice(sorted(best))

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

def calculateLocalUtility(action):

    if action["type"] == "a":
        return A

    if action["type"] == "b":
        return B

    return C


def calculateNeighborPayoff(action1, action2):

    if action1["type"] != "b" and action2["type"] != "b":

        if action1["destination"] == action2["destination"]:
            return V

        return U

    return W


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

    for iteration in range(iterations):
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

        if maxDifference < tolerance:
            break

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
