import copy
from GridContainer import GridContainer
from Player import Player
from Rule import Rule
from View import View


class Game(object):
    GAME_WIDTH = 10
    GAME_HEIGHT = 10
    GAME_MINE_COUNT = 9

    def __init__(self):
        self._players = []
        self._container = None
        self._view = None
        self._state = GameState.WaitingPlayer
        self._current_player_index = 0
        self._rule = Rule()

    def join(self, player):
        self._players.append(player)

    def run(self):
        self.join(Player("Player1"))
        self.join(Player("Player2"))
        self.init_game()
        self._view.draw_player_get_score(self._players[self._current_player_index], 0)
        while not self._state == GameState.EndGame:
            action, position = self._view.get_player_action_and_grid()
            if action == View.PlayerAction["Quit"]:
                self._view.end_game()
                self._state = GameState.EndGame
                continue
            elif action == View.PlayerAction["Replay"]:
                self.init_game()
                continue

            if self._state == GameState.WaitingReplay:
                continue

            if action == View.PlayerAction["Flag"] or action == View.PlayerAction["ClickGrid"]:
                self.player_click_or_set_flag(action, position)

    def init_game(self):
        self._state = GameState.InitGrid
        self._view = View(Game.GAME_WIDTH, Game.GAME_HEIGHT)
        container = GridContainer(Game.GAME_WIDTH, Game.GAME_HEIGHT, Game.GAME_MINE_COUNT)
        container.init_grids()
        self._container = container
        for player in self._players:
            player.reset_score()
        self._view.refresh_view(container.get_grids(), self._players)
        self._state = GameState.Playing
        self._current_player_index = 0

    def player_click_or_set_flag(self, action, position):
        touch_grids = None
        if action == View.PlayerAction["ClickGrid"]:
            touch_grids = self._container.reveal_grid_and_get_touch_grids(position)
        elif action == View.PlayerAction["Flag"]:
            touch_grids = self._container.set_flag_get_touch_grid(position)

        score = Rule.calculate_score(touch_grids, action == View.PlayerAction["ClickGrid"])

        if score == 0:
            return

        self.add_player_score(score)
        self.adjust_player_sequence()

        if self._container.is_all_grid_clicked():
            order_players = [copy.copy(p) for p in self._players]
            order_players.sort(key=lambda player: player.get_score(), reverse=True)
            self._view.draw_win(order_players[0].get_name())
            self._state = GameState.WaitingReplay

    def add_player_score(self, score):
        self._players[self._current_player_index].add_score(score)
        self._view.refresh_view(self._container.get_grids(), self._players)
        self._view.draw_player_get_score(self._players[self._current_player_index], score)

    def adjust_player_sequence(self):
        self._current_player_index += 1
        if self._current_player_index == len(self._players):
            self._current_player_index = 0


class GameState(object):
    WaitingPlayer = "WaitingPlayer"
    InitGrid = "InitGrid"
    Playing = "Playing"
    WaitingReplay = "WaitingReplay"
    EndGame = "EndGame"
