import random

from Grid import Grid
from GridContainer import GridContainer
from Player import Player
from View import View, PlayerAction


class Game(object):
    GAME_WIDTH = 10
    GAME_HEIGHT = 10
    GAME_MINE_COUNT = 9

    def __init__(self):
        self._players = []
        self._container = None
        self._view = None
        self._state = GameState.WaitingPlayer

    def join(self, player):
        self._players.append(player)

    def run(self):
        self.join(Player("Player1"))
        self.join(Player("Player2"))
        self.init_game()
        while not self._state == GameState.EndGame:
            action, click_grid = self._view.get_player_click()
            if action == PlayerAction.Quit:
                self._view.end_game()
                self._state = GameState.EndGame
                continue
            elif action == PlayerAction.Replay:
                self.init_game()
                continue
            elif action == PlayerAction.ClickGrid:
                if self._state == GameState.WaitingReplay:
                    continue
                self._container.reveal_grid(click_grid)
                self._view.refresh_view(self._container.get_grids(), self._container.get_mine_left_count())
            elif action == PlayerAction.Flag:
                if self._state == GameState.WaitingReplay:
                    continue
                self._container.set_flag(click_grid)
                self._view.refresh_view(self._container.get_grids(), self._container.get_mine_left_count())

            if self._container.check_is_game_over():
                self._container.set_all_flag_clicked()  # to check flag is correct or not
                self._view.refresh_view(self._container.get_grids(), self._container.get_mine_left_count())
                self._view.draw_game_over()
                self._state = GameState.WaitingReplay
            elif self._container.check_is_win():
                self._view.draw_win()
                self._state = GameState.WaitingReplay

    def init_game(self):
        self._state = GameState.InitGrid
        self._view = View(Game.GAME_WIDTH, Game.GAME_HEIGHT)
        container = GridContainer(Game.GAME_WIDTH, Game.GAME_HEIGHT, Game.GAME_MINE_COUNT)
        container.init_grids()
        self._container = container
        self._view.refresh_view(container.get_grids(), container.get_mine_left_count())
        self._state = GameState.Playing


class GameState(object):
    WaitingPlayer = "WaitingPlayer"
    InitGrid = "InitGrid"
    Playing = "Playing"
    WaitingReplay = "WaitingReplay"
    EndGame = "EndGame"

