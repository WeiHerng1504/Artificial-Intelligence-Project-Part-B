# COMP30024 Artificial Intelligence, Semester 1 2023
# Project Part B: Game Playing Agent

from asyncio import gather
from dataclasses import dataclass
from typing import AsyncGenerator

from .constants import *
from .hex import HexPos, HexDir
from .player import Player
from .board import Board, PlayerColor
from .actions import Action, SpawnAction, SpreadAction
from .exceptions import PlayerException, IllegalActionException
import neat


# Here we define the ADT for all possible game updates. This is a useful
# abstraction for the consumer of the game updates, as it allows them to
# pattern-match on the type of update they receive.
@dataclass
class PlayerInitialising:
    player: Player

@dataclass
class GameBegin:
    board: Board

@dataclass
class TurnBegin:
    turn_id: int
    player: Player

@dataclass
class TurnEnd:
    turn_id: int
    player: Player
    action: Action

@dataclass
class BoardUpdate:
    board: Board

@dataclass
class PlayerError:
    message: str

@dataclass
class GameEnd:
    winner: Player|None

@dataclass
class UnhandledError:
    message: str

# ADT capturing all possible game updates
GameUpdate = PlayerInitialising \
           | GameBegin \
           | TurnBegin \
           | TurnEnd \
           | BoardUpdate \
           | PlayerError \
           | UnhandledError \
           | GameEnd

import os

# Entry-point for running a game...
async def game(
    p1: Player,
    p2: Player,
) -> AsyncGenerator[GameUpdate, None]:
    """
    Run an asynchronous game sequence, yielding updates to the consumer as the
    game progresses. The consumer is responsible for handling these updates
    appropriately (e.g. logging them).
    
    """
    def eval_genomes(genomes, config):
        for i, (genome_id1, genome1) in enumerate(genomes):
            if i == len(genomes) - 1:
                break
            genome1.fitness = 0
            for genome_id2, genome2 in genomes[i+1:]:
                genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
                #game = PongGame(window, width, height)
                #game.train_ai(genome1, genome2, config)


    def calculate_fitness(self, genome1, genome2):
        pass

    def run_neat(config):
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-7')
        p = neat.Population(config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(1))

        winner = p.run(eval_genomes, 50)

    
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    run_neat(config)

    players: dict[PlayerColor, Player] = {
        player.color: player for player in [p1, p2]
    }
    assert PlayerColor.RED in players
    assert PlayerColor.BLUE in players

    board: Board = Board()
    winner_color: PlayerColor | None = None

    yield GameBegin(board)
    try:
        # Initialise the players
        yield PlayerInitialising(p1)
        async with p1:

            yield PlayerInitialising(p2)
            async with p2:
            
                # Each loop iteration is a turn.
                while True:
                    # Get the current player.
                    turn_color: PlayerColor = board._turn_color
                    player: Player = players[board._turn_color]
                    
                    # Get the current player's requested action.
                    turn_id = board.turn_count + 1
                    yield TurnBegin(turn_id, player)
                    action: Action = await player.action()
                    yield TurnEnd(turn_id, player, action)

                    # Update the board state accordingly.
                    board.apply_action(action)
                    yield BoardUpdate(board)

                    train_ai(genome1, genome2, config)

                    # Check if game is over.
                    if board.game_over:
                        winner_color = board.winner_color
                        break

                    # Update both players.
                    await p1.turn(turn_color, action)
                    await p2.turn(turn_color, action)

    except (PlayerException) as e:
        error_msg: str = e.args[0]
        if isinstance(e, IllegalActionException):
            error_msg = f"ILLEGAL ACTION: {e.args[0]}"
        else:
            error_msg = f"ERROR: {e.args[0]}"
        error_player: PlayerColor = e.args[1]
        winner_color = error_player.opponent
        yield PlayerError(error_msg)

    except Exception as e:
        # Unhandled error (possibly a referee bug), allow it through 
        # while also notifying the consumer.
        yield UnhandledError(str(e))
        raise e
        
    yield GameEnd(players[winner_color] if winner_color is not None else None)


    def train_ai(self, genome1, genome2, config):
        net1 = neat.nn.FeedForwardNetwork.create(genome1, config)
        net2 = neat.nn.FeedForwardNetwork.create(genome2, config)

        output1 = net1.activate(
                (players[PlayerColor.BLUE].action))
        output2 = net2.activate(
                (players[PlayerColor.RED].action))
        print(output1, output2)
    #     decision1 = output1.index(max(output1))

        if board.game_over:
            calculate_fitness(genome1, genome2)
            return


