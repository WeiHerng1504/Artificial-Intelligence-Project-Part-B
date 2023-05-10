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

NEUTRAL_HEXES = [HexPos(0, 0), HexPos(0, 1), HexPos(0, 2), HexPos(0, 3), HexPos(0, 4), HexPos(0, 5), HexPos(0, 6),
                 HexPos(1, 0), HexPos(1, 1), HexPos(1, 2), HexPos(1, 3), HexPos(1, 4), HexPos(1, 5), HexPos(1, 6),
                 HexPos(2, 0), HexPos(2, 1), HexPos(2, 2), HexPos(2, 3), HexPos(2, 4), HexPos(2, 5), HexPos(2, 6),
                 HexPos(3, 0), HexPos(3, 1), HexPos(3, 2), HexPos(3, 3), HexPos(3, 4), HexPos(3, 5), HexPos(3, 6),
                 HexPos(4, 0), HexPos(4, 1), HexPos(4, 2), HexPos(4, 3), HexPos(4, 4), HexPos(4, 5), HexPos(4, 6),
                 HexPos(5, 0), HexPos(5, 1), HexPos(5, 2), HexPos(5, 3), HexPos(5, 4), HexPos(5, 5), HexPos(5, 6),
                 HexPos(6, 0), HexPos(6, 1), HexPos(6, 2), HexPos(6, 3), HexPos(6, 4), HexPos(6, 5), HexPos(6, 6)]

VALID_DIRECTIONS = (HexDir.DownRight, HexDir.Down, HexDir.DownLeft, HexDir.UpLeft, HexDir.Up, HexDir.UpRight)

class Agent:

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        Initialise the agent.
        """
        self._color = color
        self.currentPlayer = None
        self.grid = {}

        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as red")
            case PlayerColor.BLUE:
                print("Testing: I am playing as blue")

    def action(self, **referee: dict) -> Action:
        """
        Return the next action to take.
        """

        # if first to spawn, always spawn center
        if len(self.grid) == 0:
            return SpawnAction(HexPos(3, 3))

        currentGrid = {PlayerColor.RED: {}, PlayerColor.BLUE: {}}

        # splitting cells for computation
        for cell in self.grid.keys():
            if self.grid[cell][0] == PlayerColor.RED:
                currentGrid[PlayerColor.RED][cell] = self.grid[cell]
            else:
                currentGrid[PlayerColor.BLUE][cell] = self.grid[cell]

        currentState = {GRID_LAYOUT: currentGrid, PREVIOUS_MOVES: [], 
                        HEURISTIC_RESULT: [], GAME_ENDED: False, IS_SPAWN_ACTION: None}


        # minimax parameters
        depth = 3
        maximise = True

        best_score, best_state = self.mini_max(currentState, depth, -math.inf, math.inf, maximise)

        if best_state != None:
            best_move = best_state[PREVIOUS_MOVES][-1]

        match self._color:
            case PlayerColor.RED:
                if best_state[IS_SPAWN_ACTION]:
                    return SpawnAction(best_move[0])
                else:
                    return SpreadAction(best_move[0], best_move[1])
            case PlayerColor.BLUE:
                if best_state[IS_SPAWN_ACTION]:
                    return SpawnAction(best_move[0])
                else:
                    return SpreadAction(best_move[0], best_move[1])


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
                    if (cell + direction*power) not in self.grid.keys():
                        self.grid[cell + direction*power] = (color, 1)

                    #in grid, add to power
                    else: 

                        # exceed maixmum, kill cell
                        if self.grid[cell + direction*power][1] == MAX_CELL_POWER:
                            self.grid.pop(cell + direction*power, None)
                            
                        # not exceed, add to powerw
                        else:
                            self.grid[cell + direction*power] = (color, \
                                        self.grid[cell + direction*power][1] + 1)

                # remove from record
                self.grid.pop(cell, None)

    # return score for a particular grid state
    def eval_func(self,state):

        score = 0
        ownCount = len(state[GRID_LAYOUT][self._color])
        opponentCount = len(state[GRID_LAYOUT][self._color.opponent])
        ownPower = sum(cell[1] for cell in state[GRID_LAYOUT][self._color].values())
        opponentPower = sum(cell[1] for cell in state[GRID_LAYOUT][self._color.opponent].values())

        if (opponentCount == 0):
            return 1000
        elif ownCount == 0:
            return -1000

        score =(3*(ownPower - opponentPower) + 2*(ownCount - opponentCount))

        return score

    # takes a state, depth limit and colour; returns best score and best move
    def mini_max(self, state, depth, alpha, beta, maximise):

        if depth == 0 or state[GAME_ENDED]:  
            return self.eval_func(state), None

        if maximise:
            player = self._color
        else:
            player = self._color.opponent

        potentialStates = self.potential_states(state, player)

        # sort to favour certain states
        potentialStates.sort(key = lambda state: state[HEURISTIC_RESULT], reverse=True)
  
        best_move = None

        # max_
        if maximise:
            best_score = -math.inf
            for child in potentialStates:
                score, _ = self.mini_max(child, depth-1, alpha, beta, False)
                if score > best_score:
                    best_score = score
                    best_move = child
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
            return best_score, best_move

        # min_
        else:
            best_score = math.inf
            for child in potentialStates:
                score, _ = self.mini_max(child, depth-1, alpha, beta, True)
                if score < best_score:
                    best_score = score
                    best_move = child
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            return best_score, best_move

    # return list of potential moves based on given state
    def potential_states(self, state, player: PlayerColor):
        potentialStates = []

        self.currentPlayer = player

        for hex in state[GRID_LAYOUT][player]:
            #generate a possible future state
            for direction in VALID_DIRECTIONS:
                newState = self.generateStateSpread(state, hex, direction, player)
                if newState:
                    potentialStates.append(newState)

        safe_spawns = NEUTRAL_HEXES
        safe_spawns = [cell for cell in safe_spawns if cell not in state[GRID_LAYOUT][self.currentPlayer.opponent].keys()]
        safe_spawns = [cell for cell in safe_spawns if cell not in state[GRID_LAYOUT][self.currentPlayer].keys()]
        
        for opp_cell in state[GRID_LAYOUT][self.currentPlayer.opponent].keys():
            # cells reachable by opponent in next move
            for power in range(1, state[GRID_LAYOUT][self.currentPlayer.opponent][opp_cell][1] + 1):
                for direction in VALID_DIRECTIONS:
                    if (opp_cell + direction*power) in safe_spawns: safe_spawns.remove(opp_cell + direction*power)

        # simulate random spawns in half of available safe spots
        spawn_count = int(len(safe_spawns) / 2)

        for _ in range(0, spawn_count):
            random.seed()
            cell = safe_spawns[random.randint(0, len(safe_spawns) - 1)]
            newState = self.generateStateSpawn(state, cell)
            potentialStates.append(newState)
            safe_spawns.remove(cell)

        return potentialStates


    # Simulate a move. (spread action)
    # Takes a state, a hexagon location and movement direction as input.
    # Returns the simulated move as a new state.
    def generateStateSpread(self, predecessor: dict[dict, list, list, bool, bool], hex: HexPos, direction: HexDir, player: PlayerColor):
        heuristicResult = [0]
        newState = copy.deepcopy(predecessor)
        newGrid = newState[GRID_LAYOUT]

        for power in range(1, newGrid[player][hex][1] + 1):
            r_new = (hex.r + direction.r * power) % 7
            q_new = (hex.q + direction.q * power) % 7
            rq_new = HexPos(r_new, q_new)

            # remove a blue hex
            if rq_new in newGrid[player.opponent]:
                heuristicResult[0] += 1
                newGrid[player].update({rq_new: (newGrid[player.opponent][rq_new])})
                newGrid[player.opponent].pop(rq_new, None)

            # update a red hex
            if rq_new in newGrid[player]:
                if newGrid[player][rq_new][1] < 6:
                    newGrid[player].update({rq_new: (player, newGrid[player][rq_new][1] + 1)})
                else:
                    newGrid[player].pop(rq_new, None)
            else:
                newGrid[PlayerColor.RED].update({rq_new : (player, 1)})

        # remove starting hex
        newGrid[player].pop((hex))

        # update heuristic
        heuristicResult.append(self.heuristic(newGrid))

        # check terminal state
        if not newGrid[player.opponent] or not newGrid[player]:
            gameEnded = True
        else:
            gameEnded = False

        newState[PREVIOUS_MOVES].append((hex, direction))

        return {GRID_LAYOUT: newGrid, PREVIOUS_MOVES: newState[PREVIOUS_MOVES], 
                HEURISTIC_RESULT: heuristicResult, GAME_ENDED: gameEnded, IS_SPAWN_ACTION: False}

    # simulate a move. (spawn action)
    # Takes a state and a hexagon location as input.
    # Returns the simulated move as a new state.
    def generateStateSpawn(self, predecessor: dict[dict, list, list, bool, bool], location: HexPos):
        heuristicResult = [0]
        newState = copy.deepcopy(predecessor)
        newGrid = newState[GRID_LAYOUT]

        # spawn a hex
        newGrid[self.currentPlayer].update({location: (self.currentPlayer, 1)})

        # update heuristic
        heuristicResult.append(self.heuristic(newGrid))

        newState[PREVIOUS_MOVES].append((location,0,0))

        return {GRID_LAYOUT: newGrid, PREVIOUS_MOVES: newState[PREVIOUS_MOVES], 
                HEURISTIC_RESULT: heuristicResult, GAME_ENDED: False, IS_SPAWN_ACTION: True}

    # own against opponent, shortest distance
    def heuristic(self, grid):
        # placeholder value to be replaced
        shortestDistance = 1000

        for blueHex in grid[self.currentPlayer.opponent].keys():
            for redHex in grid[self.currentPlayer].keys():

                manDist = [blueHex.r - redHex.r, blueHex.q - redHex.q]
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
        
        # distance made negative to help with sorting
        return shortestDistance


    # returns total power of red and blue hexes on the grid
    def totalPower(self, state):
        reds = state[GRID_LAYOUT][PlayerColor.RED]
        blues = state[GRID_LAYOUT][PlayerColor.BLUE]
        power = 0
        
        for red in reds.values():
            power += red[1]

        for blue in blues.values():
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