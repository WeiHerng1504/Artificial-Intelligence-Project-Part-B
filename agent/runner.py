class runner:
    grid = {}

    def __init__(self, agent1, agent2) -> None:
        self.grid = {}
        self.p1 = agent1
        self.p2 = agent2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.playerSymbol = 1