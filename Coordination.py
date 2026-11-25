"""
Coordination graph and Max-Plus message passing for the cleaning robots.
Authors: Adriana Sandoval Santos - A01667445
         Marbella Barba De los Santos - A01660946
         Javier Padilla Marcial - A01660945
         Camila Quintanilla Cabrera - A01662397
         Alani Daniel Garcia Maya - A01277308
Date: 2026-11-24

Two connected robots that want the same dirty cell play a 2x2 game:
G = go toward the dirty cell, Y = yield (go somewhere else).
Payoffs of one robot (the other one plays G with probability q):

              G (q)      Y (1 - q)
      G       a = A + V  b = A + U
      Y       c = C + U  d = C + U

The robots split up (one goes, one yields) only if a < c and b > d,
which gives the condition V < C + U - A. In the same way, a robot must
prefer to yield instead of moving into the cell where its neighbor
stays (for example, while cleaning): W < C + U - A. Both conditions
are checked when the module is loaded.
"""

# Parameters selected
A = 10       # Utility for moving to a dirty cell
B = 0        # Utility for not moving (staying or cleaning)
C = -1       # Utility for moving to a clean cell
D = 5        # Maximum distance between neighbors
U = 5        # Reward for choosing different destinations
V = -20      # Penalty: both move into the same cell, or same target
W = -20      # Penalty: a robot moves into the cell where its neighbor stays
Z = 0        # Payoff in any other case
K = 3        # Number of nearest dirty cells each robot considers
LAMBDA = 1   # Utility lost per extra cell of distance (vs. the nearest)

# Builds the 2x2 conflict game of two robots that want the same dirty
# cell, from the point of view of one robot.
# Parameters: None.
# Returns: Tuple (a, b, c, d):
#   a: both go (G, G); b: I go, the other yields (G, Y);
#   c: I yield, the other goes (Y, G); d: both yield (Y, Y).
def conflictGame():
    a = A + V
    b = A + U
    c = C + U
    d = C + U
    return a, b, c, d

# Calculates the mixed-strategy equilibrium of a 2x2 game, from
# a*q + b*(1 - q) = c*q + d*(1 - q).
# Parameters: a, b, c, d: Payoffs of the game (see conflictGame).
# Returns: Probability q of playing G, or None if there is no mixed
# equilibrium (one strategy is dominant or q is outside 0 < q < 1).
def mixedEquilibrium(a, b, c, d):
    denominator = (a - b) - (c - d)

    if denominator == 0:
        return None

    q = (d - b) / denominator

    if 0 < q < 1:
        return q

    return None

# Checks that the parameters make the robots split up instead of
# going to the same dirty cell: V < C + U - A (that is, a < c and
# b > d in the conflict game), and that a robot prefers to yield instead
# of moving into the cell where its neighbor stays: W < C + U - A.
# Parameters: None.
# Returns: None. Raises ValueError if the condition does not hold.
def checkParameters():
    a, b, c, d = conflictGame()

    if not (a < c and b > d):
        raise ValueError(
            f"V must be smaller than C + U - A = {C + U - A}; with "
            f"V = {V}, going to the same dirty cell is the best answer "
            "and the robots will follow each other"
        )

    if not W < C + U - A:
        raise ValueError(
            f"W must be smaller than C + U - A = {C + U - A}; with "
            f"W = {W}, a robot prefers to move into the cell where "
            "its neighbor is cleaning"
        )

# A robot yields its nearest dirty cell for another target only if the
# extra distance costs less than what it gains by avoiding the
# conflict: LAMBDA * extraDistance < U - V.
MAX_EXTRA_DISTANCE = (U - V) / LAMBDA

checkParameters()

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
# A robot standing on a dirty cell spends this step cleaning it, so its
# only action is to stay. (this only happens if it starts there, 
# since robots clean a cell as soon as they arrive)
# Parameters: agent: Robot; model: Simulation model.
# Returns: List of actions, each a dictionary with "type", "destination",
# "target" (dirty cell the robot is heading to, or None) and
# "extraDistance" (how much farther that target is than the robot's
# nearest dirty cell).
def getPossibleActions(agent, model):
    if agent.pos in model.dirtyCells:
        return [{
            "type": "b",
            "destination": agent.pos,
            "target": None,
            "extraDistance": 0
        }]

    actions = []
    getMyNeighbors = model.grid.get_neighborhood(
        agent.pos, moore=False, include_center=False
    )

    # Actions a: one step toward each of the K nearest dirty cells
    targets = sorted(
        model.dirtyCells,
        key=lambda cell: (manhattan(agent.pos, cell), cell)
    )[:K]
    dirtySteps = set()

    if targets:
        nearestDistance = manhattan(agent.pos, targets[0])

    for target in targets:
        extraDistance = manhattan(agent.pos, target) - nearestDistance

        # Only keeps alternative targets that are worth yielding for.
        if extraDistance < MAX_EXTRA_DISTANCE:
            dirtyStep = goToward(agent, target, model)
            dirtySteps.add(dirtyStep)

            actions.append({
                "type": "a",
                "destination": dirtyStep,
                "target": target,
                "extraDistance": extraDistance
            })

    # Action b: stay in the current cell
    actions.append({
        "type": "b",
        "destination": agent.pos,
        "target": None,
        "extraDistance": 0
    })

    # Action c: move to a random clean neighbor (not used by an action a)
    cleanCells = [
        cell for cell in getMyNeighbors
        if cell not in model.dirtyCells and cell not in dirtySteps
    ]

    if cleanCells:
        actions.append({
            "type": "c",
            "destination": model.random.choice(sorted(cleanCells)),
            "target": None,
            "extraDistance": 0
        })

    return actions

# Local utility q_i of one action.
# - A step toward one of the K nearest dirty cells gives A, minus LAMBDA
#   for each extra cell of distance compared with the nearest one (even
#   if the next cell is still clean).
# - Not moving (staying or cleaning) gives B.
# - Any other move gives C.
# Parameters: action: Action dictionary.
# Returns: Utility of the action.
def calculateLocalUtility(action):

    if action["type"] == "b":
        return B

    if action["type"] == "a":
        return A - LAMBDA * action["extraDistance"]

    return C

# Pairwise payoff f_ij between the actions of two neighbor robots.
# Parameters: action1, action2: Actions of the two robots.
# Returns:
#   V if both go to the same dirty cell, or both move into the same cell;
#   W if one robot moves into the cell where the other one stays
#     (for example, while it is cleaning);
#   U if both move to different cells;
#   Z otherwise.
def calculateNeighborPayoff(action1, action2):

    target1 = action1["target"]

    if target1 is not None and target1 == action2["target"]:
        return V

    bothMove = action1["type"] != "b" and action2["type"] != "b"

    if action1["destination"] == action2["destination"]:
        return V if bothMove else W

    if bothMove:
        return U

    return Z

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

                        # Adds what the other neighbors said about this
                        # action.
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

