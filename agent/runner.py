from program import Agent
from referee.game import \
    PlayerColor, Action, SpawnAction, SpreadAction, HexPos, HexDir, MAX_CELL_POWER

import neat
import os

class runner:
    grid = {}

    def __init__(self, agent1, agent2) -> None:
        self.grid = {}
        self.p1 = Agent(PlayerColor.BLUE)
        self.p2 = Agent(PlayerColor.RED)
        self.isEnd = False
        
def run_neat(config):
    #p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-7')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    # winner = p.run(eval_genomes, 1)
    # with open("best.pickle", "wb") as f:
    #     pickle.dump(winner, f)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    run_neat(config)