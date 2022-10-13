import copy

import pygame as pygame


class View(object):
    BgColor = (192, 192, 192)
    GridColor = (128, 128, 128)
    GridSize = 32  # Size of grid
    Border = 16  # Top border
    TopBorder = 100  # Left, Right, Bottom border
    ScoreWidth = 250
    FontSize = 20
    SmileHeight = 50
    ScoreMaxRow = 15
    ElementDict = {
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
    ClickGrid = "ClickGrid"
    Flag = "Flag"
    Replay = "Replay"
    Quit = "Quit"
    LeftButton = 1
    RightButton = 3

    def __init__(self, nGrid_width_count, nGrid_height_count):
        pygame.init()
        pygame.display.set_caption("MineSweeper")  # S Set the caption of window
        self._display_width = View.GridSize * nGrid_width_count + View.Border * 2 + View.ScoreWidth  # Display width
        self._display_height = View.GridSize * nGrid_height_count + View.Border + View.TopBorder  # Display height
        self._display = pygame.display.set_mode((self._display_width, self._display_height))  # Create display
        self._timer = pygame.time.Clock()
        self._grids = {}
        self._smile_rect = pygame.Rect(((self._display_width - View.ScoreWidth) - View.GridSize) / 2,
                                       View.SmileHeight,
                                       View.GridSize,
                                       View.GridSize)
        self._score_texts = []

    def RefreshView(self, grids, players):
        self._display.fill(View.BgColor)

        for g in grids.values():
            self.DrawGrid(g)
        # smile
        self._display.blit(View.ElementDict["Smile"], self._smile_rect)

        for i in range(len(players)):
            player_text = "{0}: ({1})".format(players[i].GetName(), players[i].GetScore())
            player_render = pygame.font.SysFont("Calibri", View.FontSize).render(player_text, True, (0, 0, 0))
            self._display.blit(player_render,
                               (self._display_width - View.Border - View.ScoreWidth,
                                View.Border + i * View.FontSize))

        pygame.display.update()

    def DrawGrid(self, grid):
        rect = pygame.Rect(View.Border + grid["X"] * View.GridSize,
                           View.TopBorder + grid["Y"] * View.GridSize, View.GridSize, View.GridSize)

        if grid["IsFlag"]:
            if not grid["IsMine"] and grid["IsClicked"]:
                self._display.blit(View.ElementDict["MineFalse"], rect)
            else:
                self._display.blit(View.ElementDict["Flag"], rect)
        elif grid["IsMine"]:
            if grid["IsMineClicked"]:
                self._display.blit(View.ElementDict["MineClicked"], rect)
            elif grid["IsClicked"]:
                self._display.blit(View.ElementDict["Mine"], rect)
            else:
                self._display.blit(View.ElementDict["Grid"], rect)
        elif not grid["IsClicked"]:
            self._display.blit(View.ElementDict["Grid"], rect)
        else:
            self._display.blit(View.ElementDict[grid["MineCount"]], rect)
        self._grids[(grid["X"], grid["Y"])] = rect

    def DrawPlayerGetScore(self, player, score):
        player_text = player.GetName() + " Score: " + ("+ " if score >= 0 else "- ") + str(abs(score))
        self._score_texts.append(player_text)
        for i in range(View.ScoreMaxRow):
            if i >= len(self._score_texts):
                break
            row = i if len(self._score_texts) < View.ScoreMaxRow else len(self._score_texts) - View.ScoreMaxRow + i
            add_row_text = "{0} - {1}".format(row, self._score_texts[row])
            player_render = pygame.font.SysFont("Calibri", View.FontSize).render(add_row_text, True, (0, 0, 0))
            self._display.blit(player_render,
                               (self._display_width - View.ScoreWidth, View.TopBorder + i * View.FontSize))

        pygame.display.update()

    def DrawCurrentPlayer(self, player):
        player_text = "Current Player: " + player.GetName()
        player_render = pygame.font.SysFont("Calibri", View.FontSize).render(player_text, True, (0, 0, 0))
        self._display.blit(player_render, (View.Border, View.Border))
        pygame.display.update()

    def GePlayerActionPosition(self):
        while True:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return View.Quit, None
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if self._smile_rect.collidepoint(event.pos):
                            return View.Replay, None

                        position = self.GetClickedPosition(event)
                        if position is None:
                            continue
                        elif event.button == View.LeftButton:
                            return View.ClickGrid, position
                        elif event.button == View.RightButton:
                            return View.Flag, position
            except KeyboardInterrupt:
                return View.Quit, None

    def GetClickedPosition(self, event):
        for position, rect in self._grids.items():
            if rect.collidepoint(event.pos):
                return position

    def DrawWin(self, win_player_name):
        self._display.blit(View.ElementDict["Win"], self._smile_rect)  # smile change to win
        win_str = "{} Win!!!".format(win_player_name)
        win_render = pygame.font.SysFont("Calibri", View.FontSize).render(win_str, True, (0, 0, 0))
        win_rect = win_render.get_rect()
        win_rect.center = ((self._display_width - View.Border - View.ScoreWidth) / 2,
                           View.Border + View.FontSize + View.FontSize / 2)
        self._display.blit(win_render, win_rect)
        pygame.display.update()

    def CloseWindows(self):
        pygame.quit()
