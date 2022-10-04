import pygame as pygame


class View(object):
    bg_color = (192, 192, 192)
    grid_color = (128, 128, 128)
    grid_size = 32  # Size of grid
    border = 16  # Top border
    top_border = 100  # Left, Right, Bottom border
    empty = pygame.image.load("Sprites/empty.png")
    flag = pygame.image.load("Sprites/flag.png")
    grid = pygame.image.load("Sprites/Grid.png")
    grid1 = pygame.image.load("Sprites/grid1.png")
    grid2 = pygame.image.load("Sprites/grid2.png")
    grid3 = pygame.image.load("Sprites/grid3.png")
    grid4 = pygame.image.load("Sprites/grid4.png")
    grid5 = pygame.image.load("Sprites/grid5.png")
    grid6 = pygame.image.load("Sprites/grid6.png")
    grid7 = pygame.image.load("Sprites/grid7.png")
    grid8 = pygame.image.load("Sprites/grid8.png")
    mine = pygame.image.load("Sprites/mine.png")
    mineClicked = pygame.image.load("Sprites/mineClicked.png")
    mineFalse = pygame.image.load("Sprites/mineFalse.png")
    game_over = pygame.image.load("Sprites/gameover.png")
    smile = pygame.image.load("Sprites/smile.png")
    win = pygame.image.load("Sprites/win.png")

    def __init__(self, nGridWidth, nGridHeight):
        pygame.init()
        pygame.display.set_caption("MineSweeper")  # S Set the caption of window
        self._display_width = View.grid_size * nGridWidth + View.border * 2  # Display width
        self._display_height = View.grid_size * nGridHeight + View.border + View.top_border  # Display height
        self._display = pygame.display.set_mode((self._display_width, self._display_height))  # Create display
        self._timer = pygame.time.Clock()
        self._grids = {}
        self._smile_rect = pygame.Rect((self._display_width - View.grid_size) / 2,
                                       View.border,
                                       View.grid_size,
                                       View.grid_size)

    def refresh_view(self, grids, mine_left):
        self._display.fill(View.bg_color)
        for row in grids:
            for g in row:
                self.draw_grid(g)
        # flag count
        mine_left_text = pygame.font.SysFont("Calibri", 50).render(str(mine_left), True, (0, 0, 0))
        self._display.blit(mine_left_text, (self._display_width - View.border - 50, View.border))
        # smile
        self._display.blit(View.smile, self._smile_rect)
        pygame.display.update()

    def draw_grid(self, grid):
        rect = pygame.Rect(View.border + grid.get_x() * View.grid_size,
                           View.top_border + grid.get_y() * View.grid_size, View.grid_size, View.grid_size)

        if grid.get_is_flag():
            if not grid.get_is_mine() and grid.get_is_clicked():
                self._display.blit(View.mineFalse, rect)
            else:
                self._display.blit(View.flag, rect)
        elif grid.get_is_mine():
            if grid.get_is_mine_clicked():
                self._display.blit(View.mineClicked, rect)
            elif grid.get_is_clicked():
                self._display.blit(View.mine, rect)
            else:
                self._display.blit(View.grid, rect)
        elif not grid.get_is_clicked():
            self._display.blit(View.grid, rect)
        else:
            if grid.get_mine_count() == 0:
                self._display.blit(View.empty, rect)
            elif grid.get_mine_count() == 1:
                self._display.blit(View.grid1, rect)
            elif grid.get_mine_count() == 2:
                self._display.blit(View.grid2, rect)
            elif grid.get_mine_count() == 3:
                self._display.blit(View.grid3, rect)
            elif grid.get_mine_count() == 4:
                self._display.blit(View.grid4, rect)
            elif grid.get_mine_count() == 5:
                self._display.blit(View.grid5, rect)
            elif grid.get_mine_count() == 6:
                self._display.blit(View.grid6, rect)
            elif grid.get_mine_count() == 7:
                self._display.blit(View.grid7, rect)
            elif grid.get_mine_count() == 8:
                self._display.blit(View.grid8, rect)
        self._grids[grid] = rect

    def get_player_click(self):
        while True:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return PlayerAction.Quit, None
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if self._smile_rect.collidepoint(event.pos):
                            return PlayerAction.Replay, None

                        click_grid = self.get_click_grid(event)
                        if click_grid is None:
                            continue
                        elif event.button == ButtonType.LeftButton:
                            return PlayerAction.ClickGrid, click_grid
                        elif event.button == ButtonType.RightButton:
                            return PlayerAction.Flag, click_grid
            except KeyboardInterrupt:
                return PlayerAction.Quit, None

    def get_click_grid(self, event):
        for grid, rect in self._grids.items():
            if rect.collidepoint(event.pos):
                return grid

    def draw_game_over(self):
        self._display.blit(View.game_over, self._smile_rect)  # smile change to game over
        pygame.display.update()

    def draw_win(self):
        self._display.blit(View.win, self._smile_rect)  # smile change to game over
        pygame.display.update()

    def end_game(self):
        pygame.quit()


class PlayerAction(object):
    ClickGrid = "ClickGrid"
    Flag = "Flag"
    Replay = "Replay"
    Quit = "Quit"


class ButtonType(object):
    LeftButton = 1
    RightButton = 3
