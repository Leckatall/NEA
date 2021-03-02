class Player:
    def __init__(self, id, colour):
        self.id = id
        self.colour = colour

        self.vp = 0
        self.settlements = []
        self.ports = []
        self.resources = {
            "Wood": 0,
            "Rock": 0,
            "Hay": 0,
            "Sheep": 0,
            "Clay": 0
        }
        self.cards = {
            "Knights": 0,
            "VP": 0
        }

    def victory_points(self, board):
        vp = self.vp
        if board.LargestArmyHolder == self.id:
            vp += 2

        if board.LongestRoadHolder == self.id:
            vp += 2

        return vp

    def collect(self, gamestate, roll):
        for point in self.settlements:
            self.resources[gamestate.board.points[point].land[roll]] += 1





