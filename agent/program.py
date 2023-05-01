# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent
import numpy as np
import copy
import math
import random
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
SCORE = "score"

class Agent:

    grid = {}
    
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

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
                     HEURISTIC_RESULT: [], GAME_ENDED: False, SCORE: None}

        bestStates = [startingState]
        solution = False

        # for state in bestStates:
            # potentialStates = potential_states(state, self._color)

        # changeable
        depth = 3
        
        # might be somehting like currentState other than startingState
        best_score, best_state = mini_max(startingState, depth, self._color)
        
        # format
        # best_move = (r,q,player,k)

        if best_state != None:
            best_move = best_state[PREVIOUS_MOVES][-1]

        match self._color:
            case PlayerColor.RED:
                return SpawnAction(HexPos(3, 3))
                return SpawnAction(HexPos(best_move[0],best_move[1]))
                return SpreadAction(HexPos(best_move[0],best_move[0]), HexDir)
            case PlayerColor.BLUE:
                # This is going to be invalid... BLUE never spawned!
                # return SpreadAction(HexPos(3, 3), HexDir.Up)
                return SpawnAction(HexPos(3,2))


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


# return score for a particular grid state
def eval_func(state):
    score = 0
    # difference between num of reds and blues occupied
    redCount = len(state[GRID_LAYOUT][PlayerColor.RED])
    blueCount = len(state[GRID_LAYOUT][PlayerColor.BLUE])

    # +ve means more red; -ve means more blue
    score = redCount - blueCount
    return score

# setting the color? or maximise? check ifs condition
# takes a state, depth limit and colour; returns best score and best move
def mini_max(state, depth, color: PlayerColor):
    # game ended, no red hexes or no blue hexes
    if depth == 0 or len(state[GRID_LAYOUT][PlayerColor.RED]) == 0 or len(state[GRID_LAYOUT][PlayerColor.BLUE]) == 0 :  
        return eval_func(state), None
    
    if color:
        best_score = -np.inf
        best_move = None
        for child in potential_states(state,color):
            score, _ = mini_max(child, depth-1, color != color)
            if score > best_score:
                best_score = score
                best_move = child

        return best_score, best_move

    else:
        best_score = np.inf
        best_move = None
        for child in potential_states(state,color):
            score, _ = mini_max(child, depth-1, color)
            if score < best_score:
                best_score = score
                best_move = child

        return best_score, best_move

    
# state format
# state = {gridLayout, previousMoves, heuristicResults, gameEnded, score}
# gridLayout = { red : { (r, q, p, k), ...}, blue : { (r, q, p, k), ...} }
# previousMoves = [(r, q, p, k), ...]
# heuristicResults = [int, int]
# gameEnded = bool

# where to insert generateStateSpawn?

# return list of potential moves based on given state
def potential_states( state, colour: PlayerColor):
    potentialStates = []
    validDirections = ((0, 1), (1, 0), (0, -1), (-1, 0), (1, -1), (-1, 1))

    #dont need this for loop?
    # for state in bestStates:
        # for all red hexes
    if colour == PlayerColor.RED:
        for redHex in state[GRID_LAYOUT][PlayerColor.RED]:
            #generate a possible future state
            for direction in validDirections:
                newState = generateStateSpread(state, redHex, direction,colour)
                if newState:
                    potentialStates.append(newState)
            # generateStateSpawn(state,colour)
    else:
        for blueHex in state[GRID_LAYOUT][PlayerColor.BLUE]:
            #generate a possible future state
            for direction in validDirections:
                newState = generateStateSpread(state, blueHex, direction, colour)
                if newState:
                    potentialStates.append(newState)   
            # generateStateSpawn(state,colour)

    return potentialStates


# Simulate a move. (spread action)
# changes heuristicResult[0] here, previousmove appended, gameended checked.
# Takes a state, a hexagon location and movement direction as input.
# Returns the simulated move as a new state
def generateStateSpread(predecessor: dict[dict, list, list, bool, int], hex: tuple, direction: tuple, colour:PlayerColor):

    # state format
    # state = {gridLayout, previousMoves, heuristic_results, gameEnded}

    heuristicResult = [0]
    newState = copy.deepcopy(predecessor)
    newGrid = newState["gridLayout"]

    if colour == PlayerColor.RED:
        for power in range(1, newGrid["redHexes"][hex][1] + 1):

            r_new = (hex[0] + direction[0] * power) % 7
            q_new = (hex[1] + direction[1] * power) % 7

            # remove a blue hex
            if (r_new, q_new) in newGrid["blueHexes"]:
                heuristicResult[0] += 1
                newGrid["redHexes"].update({(r_new, q_new): 
                                (newGrid["blueHexes"][(r_new, q_new)])})
                newGrid["blueHexes"].pop((r_new, q_new), None)

            # update a red hex
            if (r_new, q_new) in newGrid["redHexes"]:
                if newGrid["redHexes"][(r_new, q_new)][1] < 6:
                    newGrid["redHexes"].update({(r_new, q_new): 
                                ('r', newGrid["redHexes"][(r_new, q_new)][1] + 1)})
                else:
                    newGrid["redHexes"].pop((r_new, q_new), None)
            else:
                newGrid["redHexes"].update({(r_new, q_new) : ('r', 1)})

        # remove starting hex
        newGrid["redHexes"].pop((hex))

        # update heuristic
        heuristicResult.append(heuristic(newGrid))

        # state with no redhexes, avoid
        if not newGrid["redHexes"]:
            return None

        # terminal state?
        if not newGrid["blueHexes"]:
            gameEnded = True
        else:
            gameEnded = False

        newState["previousMoves"].append(hex + direction)

        return {"gridLayout": newGrid, "previousMoves": newState["previousMoves"], 
                "heuristicResult": heuristicResult, "gameEnded": gameEnded}
    else:
        for power in range(1, newGrid["blueHexes"][hex][1] + 1):

            r_new = (hex[0] + direction[0] * power) % 7
            q_new = (hex[1] + direction[1] * power) % 7

            # remove a red hex
            if (r_new, q_new) in newGrid["redHexes"]:
                heuristicResult[0] += 1
                newGrid["blueHexes"].update({(r_new, q_new): 
                                (newGrid["redHexes"][(r_new, q_new)])})
                newGrid["redHexes"].pop((r_new, q_new), None)

            # update a blue hex
            if (r_new, q_new) in newGrid["blueHexes"]:
                if newGrid["blueHexes"][(r_new, q_new)][1] < 6:
                    newGrid["blueHexes"].update({(r_new, q_new): 
                                ('r', newGrid["blueHexes"][(r_new, q_new)][1] + 1)})
                else:
                    newGrid["blueHexes"].pop((r_new, q_new), None)
            else:
                newGrid["blueHexes"].update({(r_new, q_new) : ('r', 1)})

        # remove starting hex
        newGrid["blueHexes"].pop((hex))

        # update heuristic
        heuristicResult.append(heuristic(newGrid))

        # state with no blueHexes, avoid
        if not newGrid["blueHexes"]:
            return None

        # terminal state?
        if not newGrid["redHexes"]:
            gameEnded = True
        else:
            gameEnded = False

        newState["previousMoves"].append(hex + direction)

        return {"gridLayout": newGrid, "previousMoves": newState["previousMoves"], 
                "heuristicResult": heuristicResult, "gameEnded": gameEnded, "score": None}


# simulate a move. (spawn action)valid?
# how to spawn? (random/)
def generateStateSpawn(predecessor: dict[dict, list, list, bool, int], color:PlayerColor):
    heuristicResult = [0]
    newState = copy.deepcopy(predecessor)
    newGrid = newState["gridLayout"]
    randnum1 = random.randrange(0,6)
    randnum2 = random.randrange(0,6)

    if color == PlayerColor.RED:
        # spawn red hex
        while totalPower(predecessor) < 49 and valid_spawn(predecessor,(randnum1,randnum2)):
            newGrid["redHexes"].update({(randnum1,randnum2) : (color, 1)})

        # update heuristic
        heuristicResult.append(heuristic(newGrid))

        # state with no redhexes, avoid
        if not newGrid["redHexes"]:
            return None

        # terminal state?
        if not newGrid["blueHexes"]:
            gameEnded = True
        else:
            gameEnded = False

        newState["previousMoves"].append(hex + direction)

        return {"gridLayout": newGrid, "previousMoves": newState["previousMoves"], 
                "heuristicResult": heuristicResult, "gameEnded": gameEnded}
    
    if color == PlayerColor.BLUE:
        # spawn blue hex
        while totalPower(predecessor) < 49 and valid_spawn(predecessor,(randnum1,randnum2)):
            newGrid["redHexes"].update({(randnum1,randnum2) : (color, 1)})

        # update heuristic
        heuristicResult.append(heuristic(newGrid))

        # state with no blueHexes, avoid
        if not newGrid["blueHexes"]:
            return None

        # terminal state?
        if not newGrid["redHexes"]:
            gameEnded = True
        else:
            gameEnded = False

        newState["previousMoves"].append(hex + direction)

        return {"gridLayout": newGrid, "previousMoves": newState["previousMoves"], 
                "heuristicResult": heuristicResult, "gameEnded": gameEnded, "score": None}
    

# red against blue
def heuristic(layout: dict[dict, dict]):

    # placeholder value to be replaced
    shortestDistance = 1000

    for blueHex in layout["blueHexes"].keys():
        for redHex in layout["redHexes"].keys():

            # manhattan distance with relative direction
            manDist = [blueHex[0] - redHex[0], blueHex[1] - redHex[1]]

            # check if wrapping is closer
            for axis in range(len(manDist)):
                if abs(manDist[axis]) > 3:
                    if manDist[axis] < 0:
                        manDist[axis] = manDist[axis] + 7
                    else:
                        manDist[axis] = manDist[axis] - 7

            # vertical 
            if manDist[0] != 0 and manDist[1] != 0 and manDist[0] / manDist[1] == -1:
                distance = abs(manDist[0])
            # closer vertically compared to horizontally
            elif manDist[0] != 0 and manDist[1] != 0 and manDist[0] / manDist[1] < 0:
                distance = math.sqrt( math.pow(manDist[0], 2) + math.pow(manDist[1], 2) - 
                            2*abs(manDist[0])*abs(manDist[1])*math.cos(1/3 * math.pi))
            # general case
            else:
                distance = math.hypot(abs(manDist[0]), abs(manDist[1]))

            # longer, ignore
            if distance > shortestDistance:
                continue
        
            # shorter, keep track
            if distance < shortestDistance:
                shortestDistance = distance

    return shortestDistance


#check for bug
def totalPower(state):
    reds = state[GRID_LAYOUT][PlayerColor.RED]
    blues = state[GRID_LAYOUT][PlayerColor.BLUE]
    power = 0
    for _, value in reds.items():
        power += value[1]

    for _, value in blues.items():
        power += value[1]
    
    return power

# check for bug
# check if location is already in state[GRID_LAYOUT], returns true if location not in.
def valid_spawn(state, location):
    grid = state[GRID_LAYOUT]
    reds = grid[PlayerColor.RED]
    blues = grid[PlayerColor.BLUE]

    for red in reds:
        if location == (red[0],red[1]):
            return False

    for blue in blues:
        if location == (blue[0],blue[1]):
            return False
    
    return True