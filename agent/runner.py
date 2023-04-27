from program import Agent
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, MAX_CELL_POWER

import neat
import os
import asyncio
import referee.game.player

from referee.game import Player, PlayerColor
from referee.log import LogStream, LogColor, LogLevel
from referee.run import game_user_wait, run_game, \
    game_commentator, game_event_logger, game_delay, output_board_updates
from referee.agent import AgentProxyPlayer
from referee.options import get_options
from pathlib import Path


class runner:
    grid = {}

    def __init__(self, agent1, agent2) -> None:
        self.grid = {}
        self.p1 = Agent(PlayerColor.BLUE)
        self.p2 = Agent(PlayerColor.RED)
        self.isEnd = False


    options = get_options()
    assert options is not None

    # Log config
    LogStream.set_global_setting("level", 
        [
            LogLevel.CRITICAL,
            LogLevel.INFO,
            LogLevel.INFO,
            LogLevel.DEBUG,
        ][options.verbosity])
    LogStream.set_global_setting("ansi", options.use_colour)
    LogStream.set_global_setting("unicode", options.use_unicode)

    # Referee log stream
    rl = LogStream("referee", LogColor.WHITE)
    rl.info("all messages printed by referee/wrapper modules begin with *")
    rl.info("(any other lines of output must be from your Agent class).")
    rl.info("\n")

    # Game log stream
    gl: LogStream | None = None
    gl_path: Path | None = None

    if options.logfile is not None:
        if options.logfile == 'stdout':
            # Standard stdout game log stream
            gl = LogStream(
                namespace="game",
                color=LogColor.YELLOW,
            )

        else:
            # File game log stream
            gl_path = Path(options.logfile)
            gl_path.parent.mkdir(parents=True, exist_ok=True)
            rl.debug(f"logging game output to '{gl_path}'")
            if gl_path.exists():
                rl.debug(f"clearing existing log file '{options.logfile}'")
                gl_path.unlink()

            def game_log_handler(message: str):
                if gl_path is not None:
                    with open(gl_path, "a") as f:
                        f.write(message + "\n")
            
            # File game log stream
            gl = LogStream(
                namespace="game", 
                ansi=False,
                handlers=[game_log_handler],
                output_namespace=False,
                output_level=False,
            )

    try:
        agents: dict[Player, dict] = {}
        for p_num, player_color in enumerate(PlayerColor, 1):
            # Import player classes
            player_loc = vars(options)[f"player{p_num}_loc"]
            player_name = f"player {p_num} [{':'.join(player_loc)}]"

            rl.info(f"wrapping {player_name} as {player_color}...")
            p: Player = AgentProxyPlayer(
                player_name,
                player_color,
                player_loc,
                time_limit=options.time,
                space_limit=options.space,
                log=LogStream(f"player{p_num}", LogColor[str(player_color)])
            )
            agents[p] = {
                "name": player_name,
                "loc": player_loc,
            }

    except KeyboardInterrupt:
        rl.info()  # (end the line)
        rl.info("KeyboardInterrupt: bye!")

        rl.critical("result: <interrupt>")
        os.kill(os.getpid(), 9)

    except Exception as e:
        rl.critical(f"unhandled exception: {str(e)}")
        rl.critical("stack trace:")
        rl.critical(">> ")
        rl.critical(">> ".join(format_tb(e.__traceback__)))
        rl.critical("\n")
        rl.critical(
            f">> Please report this error to the course staff, including\n"
            f">> the trigger and the above stack trace.")

        rl.critical(f"result: <error>")
        exit(1)


def eval_genomes(genomes, config):
    
    for i, (genome_id1, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 0
        for genome_id2, genome2 in genomes[i+1:]:
            genome2.fitness = 0 if genome2.fitness == None else genome2.fitness
            runner.train_ai(genome1, genome2)
        
def run_neat(config):
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-7')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    # p.run(eval_genomes, 50)
    winner = p.run(eval_genomes, 50)
    # with open("best.pickle", "wb") as f:
    #     pickle.dump(winner, f)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    run_neat(config)