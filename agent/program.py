# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent
import numpy as np
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, MAX_CELL_POWER


# This is the entry point for your game playing agent. Currently the agent
# simply spawns a token at the centre of the board if playing as RED, and
# spreads a token at the centre of the board if playing as BLUE. This is
# intended to serve as an example of how to use the referee API -- obviously
# this is not a valid strategy for actually playing the game!

GRID_LAYOUT = "gridLayout"
PREVIOUS_MOVES = "previousMoves"
HEURISTIC_RESULT = "heuristicResult"
GAME_ENDED = "gameEnded"

class Agent:

    grid = {}
    
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        # match color:
        #     case PlayerColor.RED:
        #         print("Testing: I am playing as red")
        #     case PlayerColor.BLUE:
        #         print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        currentGrid = {PlayerColor.RED: {}, PlayerColor.BLUE: {}}
        
        # splitting cells for computation
        for cell in self.grid.keys():
            if self.grid[cell][0] == PlayerColor.RED:
                currentGrid[PlayerColor.RED][cell] = self.grid[cell]
            else:
                currentGrid[PlayerColor.BLUE][cell] = self.grid[cell]

        startingState = {GRID_LAYOUT: currentGrid, PREVIOUS_MOVES: [], 
                     HEURISTIC_RESULT: [], GAME_ENDED: False}

        bestStates = [startingState]
        solution = False

        

        # match self._color:
        #     case PlayerColor.RED:
        #         return SpawnAction(HexPos(3, 3))
        #     case PlayerColor.BLUE:
        #         # This is going to be invalid... BLUE never spawned!
        #         return SpreadAction(HexPos(3, 3), HexDir.Up)


    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        match action:
            case SpawnAction(cell):
                self.grid[cell] = (color, 1)
                pass
            case SpreadAction(cell, direction):
                
                for power in range(1, self.grid[cell][1] + 1):
                    # if not in grid, spawn
                    if (cell + power*direction) not in self.grid:
                        self.grid[cell] = (color, 1)
                    #in grid, add to power
                    else: 
                        # exceed maixmum, kill cell
                        if self.grid[cell + power*direction] == MAX_CELL_POWER:
                            self.grid.pop(cell + power*direction, None)
                        # not exceed, add to power
                        else:
                            self.grid[cell + power*direction] = (color, self.grid[cell + power*direction][1] + 1)

                # remove from record
                self.grid.pop(cell, None)
                pass
    
    def mini_max(grid, depth, color):
        if depth == 0 """or leaf node """ :
            return eval_func(grid)
        
        if color:
            best_score = -np.inf
            best_move = None
            for move in potential_moves:
                score = mini_max(move, depth-1, color != color)
                if score > best_score:
                    best_score = score
                    best_move = move
                
                return best_score, best_move

        else:
            best_score = np.inf
            best_move = None
            for move in potential_moves:
                score = mini_max(move, depth-1, color)
                if score < best_score:
                    best_score = score
                    best_move = move

                return best_score, best_move

    # return score for a particular grid state
    def eval_func(grid):
        score = 0
        """not sure how to evaluate the grid and assign scores to it"""
        return score