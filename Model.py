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
from Agent import RobotAgent
from Coordination import buildCoordinationGraph, maxPlus


class CleaningModel(mesa.Model):
    # Creates a room, dirty cells, and robots for one simulation.
    # Parameters: numAgents: Number of robots.
    # maxSteps: Maximum number of simulation steps.
    # width: Number of columns; height: Number of rows.
    # seed: Optional random seed for reproducibility.
    # Returns: None.
    def __init__(self, numAgents=1, maxSteps=500,
                 width=30, height=20, seed=None):
        super().__init__(seed=seed)

        if numAgents not in [1, 2, 4, 8, 16]:
            raise ValueError("Number of agents must be 1, 2, 4, 8, or 16")

        if width != 30 or height != 20:
            raise ValueError("Room size must be 20x30")

        if maxSteps != 500:
            raise ValueError("Maximum steps must be 500")

        self.numAgents = numAgents
        self.maxSteps = maxSteps
        self.width = width
        self.height = height

        self.currentStep = 0
        self.totalMoves = 0
        self.completionTime = None
        self.selectedActions = {}

        self.grid = MultiGrid(width, height, torus=False)

        # Randomly selects 100 different dirty cells.
        allCells = [
            (x, y)
            for x in range(width)
            for y in range(height)
        ]

        self.dirtyCells = set(
            self.random.sample(allCells, 100)
        )

        self.initialDirtyCells = len(self.dirtyCells)

        # Selects random starting positions from clean cells.
        cleanCells = [
            cell for cell in allCells
            if cell not in self.dirtyCells
        ]

        startingPositions = self.random.sample(
            cleanCells, numAgents
        )

        # Creates robots at their selected starting positions.
        for position in startingPositions:
            agent = RobotAgent(self)
            self.grid.place_agent(agent, position)

        self.running = True

    # Activates every robot once and updates simulation time.
    # Parameters: None.
    # Returns: None.
    def step(self):
        if self.running:

            # Creates the coordination graph.
            graph = buildCoordinationGraph(self.agents)

            # Calculates the best action for each robot.
            self.selectedActions = maxPlus(
                self.agents,
                graph,
                self,
                iterations=10
            )

            # Activates every robot using its selected action.
            self.agents.shuffle_do("step")

            self.currentStep += 1

            if not self.dirtyCells:
                self.completionTime = self.currentStep
                self.running = False

            elif self.currentStep >= self.maxSteps:
                self.running = False

    # Calculates the percentage of initially dirty cells cleaned.
    # Parameters: None.
    # Returns: Float representing the cleaned percentage.
    def cleanPercentage(self):
        cleanedCells = (
            self.initialDirtyCells - len(self.dirtyCells)
        )

        return 100 * cleanedCells / self.initialDirtyCells

    # Returns the per-robot counters for the current simulation.
    # Parameters: None.
    # Returns: List of dictionaries with each robot's statistics.
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

    # Returns overall statistics for the current simulation.
    # Parameters: None.
    # Returns: Dictionary of simulation-level measurements.
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