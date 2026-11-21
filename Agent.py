"""
Cleaning robot agent using coordination.
Authors: Adriana Sandoval Santos - A01667445
         Marbella Barba De los Santos - A01660946
         Javier Padilla Marcial - A01660945
         Camila Quintanilla Cabrera - A01662397
         Alani Daniel Garcia Maya - A01277308
Date: 2026-11-06
"""

import mesa


class RobotAgent(mesa.Agent):
    # Initializes the robot's individual counters.
    # Parameters: model: Simulation model containing this robot.
    # Returns: None.
    def __init__(self, model):
        super().__init__(model)
        self.movements = 0
        self.cellsCleaned = 0
        self.actions = 0

    # Executes the action selected by the coordination algorithm.
    # Parameters: None.
    # Returns: None.
    def step(self):

        self.actions += 1

        selectedAction = self.model.selectedActions[self.unique_id]
        nextPos = selectedAction["destination"]

        # Moves the robot to its selected destination.
        if nextPos != self.pos:

            self.model.grid.move_agent(self, nextPos)

            self.movements += 1
            self.model.totalMoves += 1

        # Cleans the current cell if it is dirty.
        if self.pos in self.model.dirtyCells:

            self.model.dirtyCells.remove(self.pos)
            self.cellsCleaned += 1