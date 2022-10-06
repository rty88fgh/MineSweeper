import pygame as pygame


class View(object):
    bg_color = (192, 192, 192)
    grid_color = (128, 128, 128)
    grid_size = 32  # Size of grid
    border = 16  # Top border
    top_border = 100  # Left, Right, Bottom border
    score_width = 200
    font_size = 20
    element_dict = {
        0: pygame.image.load("Sprites/empty.png"),
        1: pygame.image.load("Sprites/grid1.png"),
        2: pygame.image.load("Sprites/grid2.png"),
        3: pygame.image.load("Sprites/grid3.png"),
        4: pygame.image.load("Sprites/grid4.png"),
        5: pygame.image.load("Sprites/grid5.png"),
        6: pygame.image.load("Sprites/grid6.png"),
        7: pygame.image.load("Sprites/grid7.png"),
        8: pygame.image.load("Sprites/grid8.png"),
        "Mine": pygame.image.load("Sprites/mine.png"),
        "MineClicked": pygame.image.load("Sprites/mineClicked.png"),
        "MineFalse": pygame.image.load("Sprites/mineFalse.png"),
        "Flag": pygame.image.load("Sprites/flag.png"),
        "Smile": pygame.image.load("Sprites/smile.png"),
        "Win": pygame.image.load("Sprites/win.png"),
        "Grid": pygame.image.load("Sprites/Grid.png"),
        "Gameover": pygame.image.load("Sprites/gameover.png")
    }
    PlayerAction = {
        "ClickGrid": "ClickGrid",
        "Flag": "Flag",
        "Replay": "Replay",
        "Quit": "Quit",
    }
    ButtonType = {
        "LeftButton": 1,
        "RightButton": 3,
    }

    def __init__(self, nGrid_width_count, nGrid_height_count):
        pygame.init()
        pygame.display.set_caption("MineSweeper")  # S Set the caption of window
        self._display_width = View.grid_size * nGrid_width_count + View.border * 2 + View.score_width  # Display width
        self._display_height = View.grid_size * nGrid_height_count + View.border + View.top_border  # Display height
        self._display = pygame.display.set_mode((self._display_width, self._display_height))  # Create display
        self._timer = pygame.time.Clock()
        self._grids = {}
        self._smile_rect = pygame.Rect(((self._display_width - View.score_width) - View.grid_size) / 2,
                                       View.border,
                                       View.grid_size,
                                       View.grid_size)

    def refresh_view(self, grids, players):
        self._display.fill(View.bg_color)

        for g in grids.values():
            self.draw_grid(g)
        # smile
        self._display.blit(View.element_dict["Smile"], self._smile_rect)

        for i in range(len(players)):
            player_text = "{0} - ({1})".format(players[i].get_name(), players[i].get_score())
            player_render = pygame.font.SysFont("Calibri", View.font_size).render(player_text, True, (0, 0, 0))
            self._display.blit(player_render,
                               (self._display_width - View.border - View.score_width,
                                View.border + i * View.font_size))

        pygame.display.update()

    def draw_grid(self, grid):
        rect = pygame.Rect(View.border + grid["X"] * View.grid_size,
                           View.top_border + grid["Y"] * View.grid_size, View.grid_size, View.grid_size)

        if grid["IsFlag"]:
            if not grid["IsMine"] and grid["IsClicked"]:
                self._display.blit(View.element_dict["MineFalse"], rect)
            else:
                self._display.blit(View.element_dict["Flag"], rect)
        elif grid["IsMine"]:
            if grid["IsMineClicked"]:
                self._display.blit(View.element_dict["MineClicked"], rect)
            elif grid["IsClicked"]:
                self._display.blit(View.element_dict["Mine"], rect)
            else:
                self._display.blit(View.element_dict["Grid"], rect)
        elif not grid["IsClicked"]:
            self._display.blit(View.element_dict["Grid"], rect)
        else:
            self._display.blit(View.element_dict[grid["MineCount"]], rect)
        self._grids[(grid["X"], grid["Y"])] = rect

    def draw_player_get_score(self, player, score):
        player_text = "player: " + player.get_name()
        player_render = pygame.font.SysFont("Calibri", View.font_size).render(player_text, True, (0, 0, 0))
        self._display.blit(player_render, (View.border, View.border))
        score_text = ("+ " if score >= 0 else "- ") + str(abs(score))
        score_render = pygame.font.SysFont("Calibri", View.font_size).render(score_text, True, (0, 0, 0))
        self._display.blit(score_render, (View.border, View.border + 20))
        pygame.display.update()

    def get_player_action_and_position(self):
        while True:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return View.PlayerAction["Quit"], None
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if self._smile_rect.collidepoint(event.pos):
                            return View.PlayerAction["Replay"], None

                        position = self.get_clicked_position(event)
                        if position is None:
                            continue
                        elif event.button == View.ButtonType["LeftButton"]:
                            return View.PlayerAction["ClickGrid"], position
                        elif event.button == View.ButtonType["RightButton"]:
                            return View.PlayerAction["Flag"], position
            except KeyboardInterrupt:
                return View.PlayerAction["Quit"], None

    def get_clicked_position(self, event):
        for position, rect in self._grids.items():
            if rect.collidepoint(event.pos):
                return position

    def draw_win(self, win_player_name):
        self._display.blit(View.element_dict["Win"], self._smile_rect)  # smile change to win
        win_str = "{} Win!!!".format(win_player_name)
        win_render = pygame.font.SysFont("Calibri", View.font_size).render(win_str, True, (0, 0, 0))
        win_rect = win_render.get_rect()
        win_rect.center = ((self._display_width - View.border - View.score_width) / 2,
                           View.border + self._smile_rect.height + View.font_size / 2)
        self._display.blit(win_render, win_rect)
        pygame.display.update()

    def end_game(self):
        pygame.quit()
