from math import cos, sin, pi
import pygame
import pygame.gfxdraw


def poly_gen(v_count, **kwargs):
    offset = kwargs.get('offset', 0)
    offset_x = kwargs.get('offset_x', offset)
    offset_y = kwargs.get('offset_y', offset)
    radius = kwargs.get('radius', 100)
    rotation = kwargs.get('rotation', 100)
    return [((radius * cos((2 * pi * i / v_count) + rotation)) + offset_x,
             (radius * sin((2 * pi * i / v_count) + rotation)) + offset_y)
            for i in range(v_count)]


def axial_to_linear(q, r):
    if r == -2:
        return q
    if r == -1:
        return 4 + q
    if r == 0:
        return 9 + q
    if r == 1:
        return 14 + q
    if r == 2:
        return 18 + q


class Render:
    def __init__(self):
        pygame.init()
        self.roll_font = pygame.font.Font('freesansbold.ttf', 36)
        self.bank_font = pygame.font.Font('freesansbold.ttf', 18)

        # Set up the drawing window
        self.screen = pygame.display.set_mode([1400, 900])

    def render(self, gamestate):
        buttons = {}

        def draw_rounded_rect(surface, rect, color, corner_radius):
            """ Draw a rectangle with rounded corners.
            Would prefer this:
                pygame.draw.rect(surface, color, rect, border_radius=corner_radius)
            but this option is not yet supported in my version of pygame so do it ourselves.

            We use anti-aliased circles to make the corners smoother

            yoinked of of stack overflow
            """
            if rect.width < 2 * corner_radius or rect.height < 2 * corner_radius:
                raise ValueError(
                    f"Both height (rect.height) and width (rect.width) must be > 2 * corner radius ({corner_radius})")

            # need to use anti aliasing circle drawing routines to smooth the corners
            pygame.gfxdraw.aacircle(surface, rect.left + corner_radius, rect.top + corner_radius, corner_radius, color)
            pygame.gfxdraw.aacircle(surface, rect.right - corner_radius - 1, rect.top + corner_radius, corner_radius,
                                    color)
            pygame.gfxdraw.aacircle(surface, rect.left + corner_radius, rect.bottom - corner_radius - 1, corner_radius,
                                    color)
            pygame.gfxdraw.aacircle(surface, rect.right - corner_radius - 1, rect.bottom - corner_radius - 1,
                                    corner_radius, color)

            pygame.gfxdraw.filled_circle(surface, rect.left + corner_radius, rect.top + corner_radius, corner_radius,
                                         color)
            pygame.gfxdraw.filled_circle(surface, rect.right - corner_radius - 1, rect.top + corner_radius,
                                         corner_radius, color)
            pygame.gfxdraw.filled_circle(surface, rect.left + corner_radius, rect.bottom - corner_radius - 1,
                                         corner_radius, color)
            pygame.gfxdraw.filled_circle(surface, rect.right - corner_radius - 1, rect.bottom - corner_radius - 1,
                                         corner_radius, color)

            rect_tmp = pygame.Rect(rect)

            rect_tmp.width -= 2 * corner_radius
            rect_tmp.center = rect.center
            pygame.draw.rect(surface, color, rect_tmp)

            rect_tmp.width = rect.width
            rect_tmp.height -= 2 * corner_radius
            rect_tmp.center = rect.center
            pygame.draw.rect(surface, color, rect_tmp)

        def click_handler(pos, player):
            # pixel to point
            # Check Points
            f = open("Points.txt", "r")
            points = [[int(i[0]), int(i[1])] for i in [x.split(",") for x in f.readlines()]]
            for index, l in enumerate(points):
                # Do x or y first?
                if pos[0] - 15 < l[0] < pos[0] + 15:
                    if pos[1] - 15 < l[1] < pos[1] + 15:
                        gamestate.board.build_settlement(gamestate, player, index)
            f.close()

            # Check Roads
            f = open("Roads.txt", "r")
            points = [[int(i[0]), int(i[1])] for i in [x.split(";")[0].split(",") for x in f.readlines()]]
            for index, l in enumerate(points):
                # Do x or y first?
                if pos[0] - 15 < l[0] < pos[0] + 15:
                    if pos[1] - 15 < l[1] < pos[1] + 15:
                        print("point:", index)
                        gamestate.board.build_road(gamestate, player, index)
            f.close()

            # check if a button within the dict was pressed
            for k in buttons.keys():
                if buttons[k].contains(pos[0] - 5, pos[1] - 5, 10, 10):
                    # Check which button
                    if k == "Next":
                        gamestate.next_turn()

        # Fill the background with white
        self.screen.fill((255, 255, 255))

        for index, cell in enumerate(gamestate.board.lands):
            # draw the land the land colour
            pygame.draw.polygon(self.screen, gamestate.board.lands[axial_to_linear(cell.q, cell.r)].colour_gen(),
                                poly_gen(6, rotation=(pi / 2), offset_x=cell.x(), offset_y=cell.y(), radius=cell.size))
            # draw the border to the land
            pygame.draw.polygon(self.screen, (100, 100, 100),
                                poly_gen(6, rotation=(pi / 2), offset_x=cell.x(), offset_y=cell.y(), radius=cell.size), width=5)

            # draw on the roll number
            text = self.roll_font.render(str(gamestate.board.lands[axial_to_linear(cell.q, cell.r)].roll), True, (0, 0, 0))
            textRect = text.get_rect()
            textRect.center = (cell.x(), cell.y())
            self.screen.blit(text, textRect)

        # draw on points
        for point in gamestate.board.points:
            radius = 15
            pygame.draw.circle(self.screen, gamestate.get_player_colour(point.settlement), (point.x, point.y), radius)

        for road in gamestate.board.roads:
            radius = 5
            pygame.draw.circle(self.screen, gamestate.get_player_colour(road.owner), (road.x, road.y), radius)

        # draw player banks
        for index, player in enumerate(gamestate.players):
            x = (index * 100) + 900
            y = 40

            text = "Player " + str(player.id) + ":"

            render_text = self.bank_font.render(text, True, (20, 20, 20))
            textRect = render_text.get_rect()
            textRect.center = (x, 20)
            self.screen.blit(render_text, textRect)

            for resource_type in player.resources.keys():
                text = resource_type + ": " + str(player.resources[resource_type])

                render_text = self.bank_font.render(text, True, (200, 150, 100))
                textRect = render_text.get_rect()
                textRect.center = (x, y)
                self.screen.blit(render_text, textRect)
                y += 15

        # draw a red box around the current player
        rect = ((gamestate.current_player * 100) + 850, 5, 100, 110)
        pygame.draw.rect(self.screen, (255, 0, 0), rect, 5, True)

        # draw next player button
        text = "Next Turn"

        render_text = self.roll_font.render(text, True, (20, 20, 20))
        textRect = render_text.get_rect()
        textRect.center = (900, 700)
        draw_rounded_rect(self.screen, textRect, (200, 200, 200), 5)
        buttons["Next"] = textRect

        self.screen.blit(render_text, textRect)

        # Did the user click the window close button?
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                click_handler(pos, gamestate.current_player)

            if e.type == pygame.QUIT:
                return False

        pygame.display.update()
        return True
