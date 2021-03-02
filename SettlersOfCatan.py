import Board
import Render
import random
from Player import Player


class Game:
    def __init__(self):
        self.player_count = int(input("Player count?\n"))
        self.current_player = 0
        self.roll = 0

        self.intro = True
        self.intro_progress = 0
        self.intro_settlement = True
        self.intro_road = True

        f = open("coloursRGB.txt", "r")
        lines = f.readlines()
        self.players = [Player(i, tuple([int(x) for x in lines[i].split(",")])) for i in range(self.player_count)]
        f.close()

        random.shuffle(self.players)

        self.render_agent = Render.Render()
        self.board = Board.Map()

    def get_player_colour(self, id):
        if id == -2:
            return 200, 50, 200
        if id == -1:
            return 150, 150, 150
        return self.players[id].colour

    def next_turn(self):
        if self.intro:
            self.intro_settlement = True
            self.intro_road = True
            self.intro_progress += 1
        self.current_player = (self.current_player + 1) % self.player_count
        self.roll = random.randint(1, 6) + random.randint(1, 6)

    def place_phase(self):
        while self.render_agent.render(self) and self.intro_progress < len(self.players) * 2:
            ...

        self.intro = False
        self.play()

    def play(self):
        self.intro = False
        print("play phase")

        while self.render_agent.render(self):
            ...


game = Game()
game.place_phase()




