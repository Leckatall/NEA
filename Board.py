from math import sqrt


def linear_to_axial(n):
    # returns q, r as a tuple
    if n <= 2:
        return n, -2
    if n <= 6:
        return n-4, -1
    if n <= 11:
        return n-9, 0
    if n <= 15:
        return n-14, 1
    if n <= 18:
        return n - 18, 2
    print("n was:", n)


class Road:
    def __init__(self, x, y, a, b):

        # x and y are the pixel location of the center of the road
        self.x = x
        self.y = y

        # a and b represent the points the road connects
        self.points = (a, b)

        self.owner = -2

    def check_for_roads_from(self, board, player):
        return board.points[self.points[0]].check_for_roads_from(player) or\
               board.points[self.points[1]].check_for_roads_from(player)

    def build(self, board, player):
        self.owner = player
        board.points[self.points[0]].roads.append({"player": player, "road": self})
        board.points[self.points[1]].roads.append({"player": player, "road": self})


class Land:
    def __init__(self, q, r, roll, resource, **kwargs):
        self.q = q
        self.r = r
        self.roll = roll
        self.resource = resource
        self.colour = self.colour_gen()
        self.size = 100

        self.offset_x = kwargs.get('offset_x', 450)
        self.offset_y = kwargs.get('offset_y', 425)

    def get_center(self):
        x = self.size * (sqrt(3) * self.q + sqrt(3) / 2 * self.r) + self.offset_x
        y = self.size * (3 / 2 * self.r) + self.offset_y
        return x, y

    def x(self):
        return self.get_center()[0]

    def y(self):
        return self.get_center()[1]

    def colour_gen(self):
        if self.resource == 1:
            return "#%02x%02x%02x" % (190, 120, 15)
        if self.resource == 2:
            return "#%02x%02x%02x" % (255, 220, 125)
        if self.resource == 3:
            return "#%02x%02x%02x" % (190, 190, 190)
        if self.resource == 4:
            return "#%02x%02x%02x" % (250, 250, 30)
        if self.resource == 5:
            return "#%02x%02x%02x" % (0, 255, 0)
        return "#%02x%02x%02x" % (50, 50, 50)


class Point:
    def __init__(self, port, lands, xy, adj):
        # Port is int
        # 0 = None
        # 1 = Mystery
        # 2 = Clay
        # 3 = Wood
        # 4 = Rock
        # 5 = Grain
        # 6 = Wool
        self.port = port
        self.settlement = -1

        self.x = int(xy[0])
        self.y = int(xy[1])

        self.land = [None] * 12
        for land in lands:
            self.land[land.roll - 1] = land.resource

        self.adjacents = adj
        self.roads = []

    def print_midpoints(self, board):
        for adj in self.adjacents:
            x = int((self.x + board.points[adj].x) / 2)
            y = int((self.y + board.points[adj].y) / 2)
            print(x, y, adj)

    def check_for_roads_from(self, player):
        for road in self.roads:
            if road["player"] == player:
                return True
        return False


class Map:
    def __init__(self):
        self.points = [None] * 54
        self.lands = []
        self.roads = []
        f = open("land.txt", "r")
        lines = f.readlines()[:19]
        for index, line in enumerate(lines):
            l = line.split(";")
            q, r = linear_to_axial(index)
            roll = int(l[0])
            resource = int(l[1])
            self.lands.append(Land(q, r, roll, resource))
        f.close()

        f = open("board.txt", "r")
        lines = f.readlines()[:54]
        g = open("Points.txt", "r")
        point_coords = g.readlines()
        for index, line in enumerate(lines):
            p = line.split(";")
            adjacent_points = [int(x) for x in p[0].split(",")]
            lands = [self.lands[int(x)] for x in p[1].split(",")]
            port = p[2]

            self.points[index] = Point(port, lands, point_coords[index].split(","), adjacent_points)
        f.close()
        g.close()

        f = open("Roads.txt", "r")
        points = [(int(p[0]), int(p[1])) for p in
                  [p.split(";")[0].split(",") for p in f.readlines()]]

        f.close()

        f = open("Roads.txt", "r")

        connections = [(int(p[0]), int(p[1])) for p in
                       [p.split(";")[1].split(",") for p in f.readlines()]]
        for i in range(len(connections)):
            x = points[i][0]
            y = points[i][1]
            a = connections[i][0]
            b = connections[i][1]
            self.roads.append(Road(x, y, a, b))

        f.close()

    def print_midpoints(self):
        for point in self.points:
            point.print_midpoints(self)

    def build_settlement(self, gamestate, player, point_id):

        # check that their are no neighboring settlements
        for p in self.points[point_id].adjacents:
            if self.points[p].settlement != -1:
                return False

        # Give them the settlement for free at the start of the game
        if gamestate.intro:
            if gamestate.intro_settlement:
                gamestate.intro_settlement = False

                self.points[point_id].settlement = player
                gamestate.players[player].settlements.append(point_id)
                return True

        # check the player has enough resources
        if gamestate.players[player].resources["Wood"] < 1:
            return False
        if gamestate.players[player].resources["Hay"] < 1:
            return False
        if gamestate.players[player].resources["Brick"] < 1:
            return False
        if gamestate.players[player].resources["Sheep"] < 1:
            return False

        if not self.points[point_id].check_for_roads_from(player):
            return False

        # Make the player pay for the settlement
        gamestate.players[player].resources["Wood"] -= 1
        gamestate.players[player].resources["Hay"] -= 1
        gamestate.players[player].resources["Brick"] -= 1
        gamestate.players[player].resources["Sheep"] -= 1

        # build the settlement
        self.points[point_id].settlement = player
        gamestate.players[player].settlements.append(point_id)
        return True

    def build_road(self, gamestate, player, road_id):
        points = self.roads[road_id].points
        # check that there is at least one neighboring settlement owned by the player
        # OR
        # a road next to one of the adjacent points owned by the player
        # very dense. Should probably rework
        if (self.points[points[0]].settlement != player and self.points[points[1]].settlement != player) and not (self.roads[road_id].check_for_roads_from(self, player)):
            return False

        if gamestate.intro:
            if gamestate.intro_road:
                gamestate.intro_road = False

                self.roads[road_id].build(self, player)

                return True

        # check the player has enough resources
        if gamestate.players[player].resources["Wood"] < 1:
            return False
        if gamestate.players[player].resources["Brick"] < 1:
            return False

        # Make the player pay for the settlement
        gamestate.players[player].resources["Wood"] -= 1
        gamestate.players[player].resources["Brick"] -= 1

        self.roads[road_id].build(self, player)

    def build_city(self, gamestate, player, point_id):
        # check if the building there exists/belongs to the player
        if self.points[point_id].settlement != player:
            return False

        # check the player has enough resources
        if gamestate.players[player].resources["Rock"] < 3:
            return False
        if gamestate.players[player].resources["Hay"] < 2:
            return False

        # Make the player pay for the settlement
        gamestate.players[player].resources["Rock"] -= 3
        gamestate.players[player].resources["Hay"] -= 2



