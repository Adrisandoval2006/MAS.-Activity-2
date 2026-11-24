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
    # Initializes the grid, dirty cells, and cleaning robots.
    # Parameters: 
    #   numAgents: Number of robots in the simulation.
    #   maxSteps: Maximum number of simulation steps.
    #   width: Number of grid columns.
    #   height: Number of grid rows.
    #   nDirty: Number of initially dirty cells.
    #   agentType: Coordination method ("maxplus" or "random").
    #   seed: Optional random seed for reproducibility.
    # Returns: None.
    def __init__(self, numAgents=1, maxSteps=500,
                 width=30, height=20, nDirty = 100, agentType= "maxplus", seed=None):
        super().__init__(seed=seed)

        if numAgents not in [1, 2, 4, 8, 16]:
            raise ValueError("Number of agents must be 1, 2, 4, 8, or 16")

        if width != 30 or height != 20:
            raise ValueError("Room size must be 20x30")

        if maxSteps != 500:
            raise ValueError("Maximum steps must be 500")

        if agentType not in ["maxplus", "random"]:
            raise ValueError(
                "Agent type must be 'maxplus' or 'random'"
            )

        if nDirty < 1 or nDirty > width * height - numAgents:
            raise ValueError(
                "Number of dirty cells must allow clean starting positions"
            )
        
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

        # Creates a list of all positions in the grid.
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

        # Finds clean cells available for robot placement.
        cleanCells = [
            cell for cell in allCells
            if cell not in self.dirtyCells
        ]

        # Assigns different random clean starting positions.
        startingPositions = self.random.sample(
            cleanCells, numAgents
        )

        # Creates the selected type of cleaning robots.
        agentClass = RobotAgent if agentType == "maxplus" else RandomRobotAgent
        for position in startingPositions:
            agent = agentClass(self)
            self.grid.place_agent(agent, position)

        self.running = True

     # Executes one simulation step and checks termination.
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