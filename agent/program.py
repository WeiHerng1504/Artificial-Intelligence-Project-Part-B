# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent
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
IS_SPAWN_ACTION = "isSpawnAction"

class Agent:

    # grid = {}
    #     
    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color

        #TBD
        self.grid = {}
        self.currentState = {GRID_LAYOUT: {PlayerColor.RED: {}, PlayerColor.BLUE: {}}, PREVIOUS_MOVES: [], 
                             HEURISTIC_RESULT: [], GAME_ENDED: False, IS_SPAWN_ACTION: None}
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """
        print("action " + str(self._color) + "\n")

        #don't need this?
        # currentGrid = {PlayerColor.RED: {}, PlayerColor.BLUE: {}}


        # # splitting cells for computation
        # for cell in self.grid.keys():
        #     if self.grid[cell][0] == PlayerColor.RED:
        #         currentGrid[PlayerColor.RED][cell] = self.grid[cell]
        #     else:
        #         currentGrid[PlayerColor.BLUE][cell] = self.grid[cell]

        # don't need this?
        # currentState = {GRID_LAYOUT: currentGrid, PREVIOUS_MOVES: [], 
        #              HEURISTIC_RESULT: [], GAME_ENDED: False, IS_SPAWN_ACTION: None}

        bestStates = [self.currentState]
        solution = False

        # # run a heuristic comparison
        # # heuristic has two components, 
        # # first item is hexes converted, 
        # # second item is shortest straight line distance
        # # we prioritize first item

        # # placeholder values to be replaced
        # bestHeuristic = [0, 1000]

        # for state in potentialMoves:
        #     # solution found
        #     if state["gameEnded"]:
        #         solution = state["previousMoves"]
        #         break

        #     # converts more hexes
        #     if state["heuristicResult"][0] > bestHeuristic[0]:
        #         bestHeuristic = state["heuristicResult"]
        #         continue

        #     # shorter distance
        #     if state["heuristicResult"][0] == bestHeuristic[0] and state["heuristicResult"][1] < bestHeuristic[1]:
        #         bestHeuristic = state["heuristicResult"]


        # # keeping only desirable nodes
        # if not solution:
        #     bestStates = [state for state in potentialMoves if state["heuristicResult"] == bestHeuristic]

        # changeable
        depth = 3
        maximise = True

        best_score, best_state = self.mini_max(self.currentState, depth, maximise)
        
        self.currentState = best_state
        # print(self.grid)
        # print(self.currentState)
        # format
        # best_move = (hexPos,dr,dq)

        if best_state != None:
            best_move = best_state[PREVIOUS_MOVES][-1]
        print(best_move)
        
        match self._color:
            case PlayerColor.RED:
                # return(SpawnAction(HexPos(3,3)))
                if best_state[IS_SPAWN_ACTION]:
                    return SpawnAction(best_move[0])
                else:
                    return SpreadAction(best_move[0], best_move[1])
            case PlayerColor.BLUE:
                # This is going to be invalid... BLUE never spawned!
                # return(SpawnAction(HexPos(3,2)))
                if best_state[IS_SPAWN_ACTION]:
                    return SpawnAction(best_move[0])
                else:
                    return SpreadAction(best_move[0], best_move[1])


    def turn(self, color: PlayerColor, action: Action, **referee: dict):
        """
        Update the agent with the last player's action.
        """
        print("turn " + str(self._color) + "\n")
        # print(self.grid)
        match action:
            case SpawnAction(cell):
                self.grid[cell] = (color, 1)

                pass
            case SpreadAction(cell, direction):
                
                for power in range(1, self.grid[cell][1] + 1):
                    # if not in grid, spawn
                    if (cell + direction*power) not in self.grid:
                        self.grid[cell] = (color, 1)
                    #in grid, add to power
                    else: 
                        # exceed maixmum, kill cell
                        if self.grid[cell + direction*power] == MAX_CELL_POWER:
                            self.grid.pop(cell + direction*power, None)
                        # not exceed, add to power
                        else:
                            self.grid[cell + direction*power] = (color, self.grid[cell + direction*power][1] + 1)

                # remove from record
                self.grid.pop(cell, None)
                # pass
        print(self.grid)



    # return score for a particular grid state
    def eval_func(self,state):
        score = 0
        # difference between num of owns and opponents occupied
        ownCount = len(state[GRID_LAYOUT][self._color])
        opponentCount = len(state[GRID_LAYOUT][self._color.opponent])

        # ownPower = 
        # opponentPower = 
        # +ve means more owns; -ve means more opponents
        score = ownCount - opponentCount 
        # score = ownPower - opponentPower
        return score

    # setting the color? or maximise? check ifs condition
    # takes a state, depth limit and colour; returns best score and best move
    def mini_max(self, state, depth, maximise):

        # game ended, no red hexes or no blue hexes
        if depth == 0: #or state[GAME_ENDED]:  
            return self.eval_func(state), None
        
        best_move = None
        #True
        if maximise:
            best_score = -math.inf
            # best_move = None
            for child in self.potential_states(state):
                score, _ = self.mini_max(child, depth-1, False)
                if score > best_score:
                    best_score = score
                    best_move = child

            return best_score, best_move

        #False
        else:
            best_score = math.inf
            # best_move = None
            for child in self.potential_states(state):
                score, _ = self.mini_max(child, depth-1, True)
                if score < best_score:
                    best_score = score
                    best_move = child

            return best_score, best_move

        
    # state format
    # state = {gridLayout, previousMoves, heuristicResults, gameEnded, isSpawnAction}
    # gridLayout = { red : { HexPos:(p, k), ...}, blue : { HexPos:(p, k), ...} }
    # previousMoves = [(HexPos, dr, dq), ...]
    # heuristicResults = [int, int]
    # gameEnded = bool

    # where to insert generateStateSpawn?

    # return list of potential moves based on given state (spawn a own hex for every existing own hex) e.g.:2 red -> spawn 2 red
    def potential_states(self, state):
        potentialStates = []
        # validDirections = ((0, 1), (1, 0), (0, -1), (-1, 0), (1, -1), (-1, 1))
        validDirections = (HexDir.DownRight, HexDir.Down, HexDir.DownLeft, HexDir.UpLeft, HexDir.Up, HexDir.UpRight)
        # currentPlayer = 
        #dont need this for loop?
        # for state in bestStates:
        # if self._color:
        for hex in state[GRID_LAYOUT][self._color]:
            #generate a possible future state
            for direction in validDirections:
                newState = self.generateStateSpread(state, hex, direction)
                if newState:
                    potentialStates.append(newState)
            
        newState = self.generateStateSpawn(state)
        potentialStates.append(newState)
        # :
        #     for blueHex in state[GRID_LAYOUT][PlayerColor.BLUE]:
        #         #generate a possible future state
        #         for direction in validDirections:
        #             newState = self.generateStateSpread(state, blueHex, direction, colour)
        #             if newState:
        #                 potentialStates.append(newState)   
                
        #         # generateStateSpawn(state,colour)

        return potentialStates


    # Simulate a move. (spread action)
    # Takes a state, a hexagon location and movement direction as input.
    # Returns the simulated move as a new state
    def generateStateSpread(self, predecessor: dict[dict, list, list, bool, bool], hex:HexPos, direction):

        # state format
        # state = {gridLayout, previousMoves, heuristic_results, gameEnded}
        heuristicResult = [0]
        newState = copy.deepcopy(predecessor)
        newGrid = newState[GRID_LAYOUT]

        if self._color == PlayerColor.RED:
            for power in range(1, newGrid[PlayerColor.RED][hex][1] + 1):
                
                r_new = (hex.r + direction.r * power) % 7
                # r_new = (hex.r + direction[0] * power) % 7
                q_new = (hex.q + direction.q * power) % 7
                # q_new = (hex.q + direction[1] * power) % 7
                rq_new = HexPos(r_new,q_new)
                # remove a blue hex
                if rq_new in newGrid[PlayerColor.BLUE]:
                    heuristicResult[0] += 1
                    newGrid[PlayerColor.RED].update({rq_new:
                                    (newGrid[PlayerColor.BLUE][rq_new])})
                    newGrid[PlayerColor.BLUE].pop(rq_new, None)

                # update a red hex
                if rq_new in newGrid[PlayerColor.RED]:
                    if newGrid[PlayerColor.RED][rq_new][1] < 6:
                        newGrid[PlayerColor.RED].update({rq_new: 
                                    (PlayerColor.RED, newGrid[PlayerColor.RED][rq_new][1] + 1)})
                    else:
                        newGrid[PlayerColor.RED].pop(rq_new, None)
                else:
                    newGrid[PlayerColor.RED].update({rq_new : (PlayerColor.RED, 1)})

            # remove starting hex
            newGrid[PlayerColor.RED].pop((hex))

            # update heuristic
            heuristicResult.append(self.heuristic(newGrid))

            # state with no redhexes, avoid
            if not newGrid[PlayerColor.RED]:
                return None

            # terminal state?
            # if not newGrid[PlayerColor.BLUE]:
            #     gameEnded = True
            # else:
            #     gameEnded = False

            newState["previousMoves"].append((hex,direction))

            return {"gridLayout": newGrid, "previousMoves": newState["previousMoves"], 
                    "heuristicResult": heuristicResult, "gameEnded": True, "isSpawnAction":False}
        
        if self._color == PlayerColor.BLUE:
            for power in range(1, newGrid[PlayerColor.BLUE][hex][1] + 1):

                r_new = (hex.r + direction.r * power) % 7
                # r_new = (hex.r + direction[0] * power) % 7
                q_new = (hex.q + direction.q * power) % 7
                # q_new = (hex.q + direction[1] * power) % 7
                rq_new = HexPos(r_new,q_new)
                
                # remove a red hex
                if rq_new in newGrid[PlayerColor.RED]:
                    heuristicResult[0] += 1
                    newGrid[PlayerColor.BLUE].update({rq_new: 
                                    (newGrid[PlayerColor.RED][rq_new])})
                    newGrid[PlayerColor.RED].pop(rq_new, None)

                # update a blue hex
                if rq_new in newGrid[PlayerColor.BLUE]:
                    if newGrid[PlayerColor.BLUE][rq_new][1] < 6:
                        newGrid[PlayerColor.BLUE].update({rq_new: 
                                    (PlayerColor.BLUE, newGrid[PlayerColor.BLUE][rq_new][1] + 1)})
                    else:
                        newGrid[PlayerColor.BLUE].pop(rq_new, None)
                else:
                    newGrid[PlayerColor.BLUE].update({rq_new : (PlayerColor.BLUE, 1)})

            # remove starting hex
            newGrid[PlayerColor.BLUE].pop((hex))

            # update heuristic
            heuristicResult.append(self.heuristic(newGrid))

            # state with no blueHexes, avoid
            if not newGrid[PlayerColor.BLUE]:
                return None

            # terminal state?
            if not newGrid[PlayerColor.RED]:
                gameEnded = True
            else:
                gameEnded = False

            newState["previousMoves"].append((hex,direction))

            return {"gridLayout": newGrid, "previousMoves": newState["previousMoves"], 
                    "heuristicResult": heuristicResult, "gameEnded": True, "isSpawnAction": False}


    # simulate a move. (spawn action)
    def generateStateSpawn(self, predecessor: dict[dict, list, list, bool, bool]):
        heuristicResult = [0]
        newState = copy.deepcopy(predecessor)
        newGrid = newState[GRID_LAYOUT]
        isSpawnAction = False

        if self._color == PlayerColor.RED:
            # try to spawn red hex with random position 
            while not isSpawnAction:
                randnum1 = random.randint(0,6)
                randnum2 = random.randint(0,6)
                hex = HexPos(randnum1,randnum2)

                if self.totalPower(predecessor) < 49 and self.valid_spawn(predecessor,hex):

                    newGrid[PlayerColor.RED].update({hex: (PlayerColor.RED, 1)})
                    isSpawnAction = True

            # update heuristic
            heuristicResult.append(self.heuristic(newGrid))

            # # state with no redhexes, avoid
            # if not newGrid[PlayerColor.RED]:
            #     return None

            # # terminal state?
            # if not newGrid[PlayerColor.BLUE]:
            #     gameEnded = True
            # else:
            #     gameEnded = False

            # edit this
            # print(tuple(hex) + (0,0))

            newState["previousMoves"].append((hex,0,0))

            return {"gridLayout": newGrid, "previousMoves": newState["previousMoves"], 
                    "heuristicResult": heuristicResult, "gameEnded": False, "isSpawnAction": isSpawnAction}
        
        if self._color == PlayerColor.BLUE:
            # try to spawn blue hex with random position
            while not isSpawnAction:
                randnum1 = random.randint(0,6)
                randnum2 = random.randint(0,6)
                hex = HexPos(randnum1,randnum2)

                if self.totalPower(predecessor) < 49 and self.valid_spawn(predecessor, hex):
                    newGrid[PlayerColor.BLUE].update({hex : (PlayerColor.BLUE, 1)})
                    isSpawnAction = True

            # update heuristic
            heuristicResult.append(self.heuristic(newGrid))

            # # state with no blueHexes, avoid
            # if not newGrid[PlayerColor.BLUE]:
            #     return None

            # # terminal state?
            # if not newGrid[PlayerColor.RED]:
            #     gameEnded = True
            # else:
            #     gameEnded = False

            #edit this
            newState["previousMoves"].append((hex,0,0))

            return {"gridLayout": newGrid, "previousMoves": newState["previousMoves"], 
                    "heuristicResult": heuristicResult, "gameEnded": False, "isSpawnAction": isSpawnAction}
        

    # own against opponent, shortest distance
    def heuristic(self, grid):

        # placeholder value to be replaced
        shortestDistance = 1000

        for blueHex in grid[self._color.opponent].keys():
            for redHex in grid[self._color].keys():

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


    # returns total pow er of red and blue hexes on the grid
    def totalPower(self, state):
        reds = state[GRID_LAYOUT][PlayerColor.RED]
        blues = state[GRID_LAYOUT][PlayerColor.BLUE]
        # redPower = 0
        # bluePower = 0
        power = 0
        for red in reds.values():
            # redPower += red[1]
            power += red[1]

        for blue in blues.values():
            # bluePower += blue[1]
            power += blue[1]

        return power

    # check if position is already in state[GRID_LAYOUT], returns true if location not in.
    def valid_spawn(self, state, position):
        grid = state[GRID_LAYOUT]
        reds = grid[PlayerColor.RED]
        blues = grid[PlayerColor.BLUE]

        for red in reds.keys():
            if position.r == red.r and position.q == red.q:
                return False

        for blue in blues.keys():
            if position.r == blue.r and position.q == blue.q:
                return False
        
        return True