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


def getPossibleActions(agent, model):
    x, y = agent.pos
    allCells = [
        (i, j)
        for i in range(model.width)
        for j in range(model.height)
    ]

    actions = []

    # Action a: move to the nearest dirty cell
    if model.dirtyCells:
        dirtyTarget = min(
            model.dirtyCells,
            key=lambda cell: (
                abs(x - cell[0]) + abs(y - cell[1]),
                cell
            )
        )
        actions.append({
            "type": "a",
            "destination": dirtyTarget
        })

    # Action b: stay in the current cell
    actions.append({
        "type": "b",
        "destination": agent.pos
    })

    # Action c: move to the nearest clean cell
    cleanCells = [
        cell for cell in allCells
        if cell not in model.dirtyCells and cell != agent.pos
    ]

    if cleanCells:

        cleanTarget = min(
            cleanCells,
            key=lambda cell: (
                abs(x - cell[0]) + abs(y - cell[1]),
                cell
            )
        )

        actions.append({
            "type": "c",
            "destination": cleanTarget
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

def maxPlus(agents, graph, model, iterations=10):

    actions = {}

    for agent in agents:
        actions[agent.unique_id] = getPossibleActions(agent, model)

    messages = {}

    for robot in graph:
        for neighbor in graph[robot]:
            messages[(robot, neighbor)] = [
                0 for _ in actions[neighbor]
            ]

    for _ in range(iterations):

        newMessages = {}

        for robot in graph:

            for neighbor in graph[robot]:

                message = []

                for neighborAction in actions[neighbor]:

                    bestValue = float("-inf")

                    for i in range(len(actions[robot])):

                        robotAction = actions[robot][i]

                        value = calculateLocalUtility(robotAction)

                        for otherRobot in graph[robot]:

                            if otherRobot != neighbor:
                                value += messages[(otherRobot, robot)][i]

                        value += calculateNeighborPayoff(
                            robotAction,
                            neighborAction
                        )

                        if value > bestValue:
                            bestValue = value

                    message.append(bestValue)

                newMessages[(robot, neighbor)] = message

        messages = newMessages

    # Select the best action for each robot
    selectedActions = {}

    for robot in graph:

        bestValue = float("-inf")
        bestAction = actions[robot][0]

        for i in range(len(actions[robot])):

            action = actions[robot][i]

            value = calculateLocalUtility(action)

            for neighbor in graph[robot]:
                value += messages[(neighbor, robot)][i]

            if value > bestValue:
                bestValue = value
                bestAction = action

        selectedActions[robot] = bestAction

    return selectedActions