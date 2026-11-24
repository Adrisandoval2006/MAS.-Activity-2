"""
Simulation model for coordinated cleaning robots.
Authors: Adriana Sandoval Santos - A01667445
         Marbella Barba De los Santos - A01660946
         Javier Padilla Marcial - A01660945
         Camila Quintanilla Cabrera - A01662397
         Alani Daniel Garcia Maya - A01277308
Date: 2026-11-21
"""

import mesa
from mesa.space import MultiGrid
from Agent import RobotAgent, RandomRobotAgent
from Coordination import buildCoordinationGraph, maxPlus


class CleaningModel(mesa.Model):
    # Creates a room, dirty cells, and robots for one simulation.
    # Parameters: numAgents: Number of robots.
    # maxSteps: Maximum number of simulation steps.
    # width: Number of columns; height: Number of rows.
    # nDirty: Number of initially dirty cells.
    # agentType: "maxplus" (coordinated robots) or "random" (M1 robots).
    # startAtOrigin: If True, every robot starts at cell [1,1], i.e.
    # (0, 0) in Mesa; otherwise each starts at a random clean cell.
    # seed: Optional random seed for reproducibility.
    # Returns: None.
    def __init__(self, numAgents=1, maxSteps=500, width=30, height=20,
                 nDirty=100, agentType="maxplus", startAtOrigin=False,
                 seed=None):
        super().__init__(seed=seed)

        if agentType not in ["maxplus", "random"]:
            raise ValueError('Agent type must be "maxplus" or "random"')

        if numAgents < 1:
            raise ValueError("There must be at least one robot")

        if width < 1 or height < 1:
            raise ValueError("Room width and height must be positive")

        if maxSteps < 1:
            raise ValueError("Maximum steps must be positive")

        if not 0 <= nDirty <= width * height:
            raise ValueError("Dirty cells must be between 0 and M x N")

        if not startAtOrigin and nDirty + numAgents > width * height:
            raise ValueError("Not enough clean cells for the robots")

        self.numAgents = numAgents
        self.maxSteps = maxSteps
        self.width = width
        self.height = height
        self.agentType = agentType

        self.currentStep = 0
        self.totalMoves = 0
        self.completionTime = None
        self.selectedActions = {}

        self.grid = MultiGrid(width, height, torus=False)

        # Randomly selects nDirty different dirty cells (100 by default).
        allCells = [
            (x, y)
            for x in range(width)
            for y in range(height)
        ]

        # Selects different dirty cells without replacement.
        self.dirtyCells = set(
            self.random.sample(allCells, nDirty)
        )

        self.initialDirtyCells = len(self.dirtyCells)

        if startAtOrigin:
            # Every robot starts at cell [1,1].
            startingPositions = [(0, 0)] * numAgents
        else:
            # Selects random starting positions from clean cells.
            cleanCells = [
                cell for cell in allCells
                if cell not in self.dirtyCells
            ]

            startingPositions = self.random.sample(
                cleanCells, numAgents
            )

        # Creates the selected type of cleaning robots.
        agentClass = RobotAgent if agentType == "maxplus" else RandomRobotAgent
        for position in startingPositions:
            agent = agentClass(self)
            self.grid.place_agent(agent, position)

        self.running = True

        # A room with no dirt is already clean at time 0.
        if not self.dirtyCells:
            self.completionTime = 0
            self.running = False

    # Computes the Max-Plus actions (coordinated robots only), activates
    # every robot once, and updates simulation time.
    # Parameters: None.
    # Returns: None.
    def step(self):
        if self.running:
            if self.agentType == "maxplus":
                # Builds the graph using current robot positions.
                graph = buildCoordinationGraph(list(self.agents))

                # Computes coordinated actions before movement.
                self.selectedActions = maxPlus(list(self.agents), graph, self)

            # Activates every robot once in random order.
            self.agents.shuffle_do("step")

            self.currentStep += 1

            if not self.dirtyCells:
                self.completionTime = self.currentStep
                self.running = False

            elif self.currentStep >= self.maxSteps:
                self.running = False

    # Calculates the percentage of initially dirty cells.
    # Parameters: None.
    # Returns:  Percentage of initially dirty cells cleaned
    def cleanPercentage(self):
        if self.initialDirtyCells == 0:
            return 100.0

        cleanedCells = (
            self.initialDirtyCells - len(self.dirtyCells)
        )

        return 100 * cleanedCells / self.initialDirtyCells

    # Collects the statistics of each cleaning robot.
    # Parameters: None.
    # Returns: List of dictionaries containing robot statistics.
    def getAgentStats(self):
        agentStats = []

        for agent in self.agents:
            agentStats.append({
                "agentId": agent.unique_id,
                "activeSteps": agent.actions,
                "movements": agent.movements,
                "cellsCleaned": agent.cellsCleaned
            })

        return agentStats

    # Collects the overall statistics of the simulation.
    # Parameters: None.
    # Returns: Dictionary containing simulation measurements.
    def getStats(self):
        return {
            "executionTime": self.currentStep,
            "completionTime": self.completionTime,
            "maxSteps": self.maxSteps,
            "cleanedPercentage": self.cleanPercentage(),
            "remainingDirtyCells": len(self.dirtyCells),
            "totalMoves": self.totalMoves,
            "allClean": self.completionTime is not None
        }
    