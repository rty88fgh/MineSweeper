import copy

from Computer import Computer
from GridManager import GridManager
from Player import Player
from View import View


class Game(object):
    InitGrid = "InitGrid"
    WaitingPlayer = "WaitingPlayer"
    Playing = "Playing"
    WaitingReplay = "WaitingReplay"
    EndGame = "EndGame"

    def __init__(self, width, height, mine_count):
        self._players = []
        self._gridManager = None
        self._view = None
        self._state = Game.InitGrid
        self._current_player_index = 0
        self._mine_count = mine_count
        self._initGame(width, height)

    def _join(self, player):
        self._players.append(player)

    def _initGame(self, width, height):
        self._width = width
        self._height = height
        self._state = Game.InitGrid
        self._view = View(self._width, self._height)
        self._gridManager = GridManager(self._width, self._height, self._mine_count)
        self._view.RefreshView(self._gridManager.GetGrids(), self._players)
        self._state = Game.Playing
        self._current_player_index = 0
        for player in self._players:
            player.ResetScore()
        self._view.RefreshView(self._gridManager.GetGrids(), self._players)

    def _processPlayerAction(self, action, position):
        score = 0
        if action == View.ClickGrid:
            score = self._gridManager.RevealGrid(position)
        elif action == View.Flag:
            score = self._gridManager.MarkGrid(position)

        if score == 0:
            return

        assert score != []

        self._addPlayerScore(score)
        self._adjustPlayerSequence()

        if self._gridManager.IsAllGridsClicked():
            order_players = [copy.copy(p) for p in self._players]
            order_players.sort(key=lambda player: player.GetScore(), reverse=True)
            self._view.DrawWin(order_players[0].GetName())
            self._state = Game.WaitingReplay

    def _addPlayerScore(self, score):
        if score < 0:
            self._players[self._current_player_index].SubScore(abs(score))
        else:
            self._players[self._current_player_index].AddScore(abs(score))

        self._view.RefreshView(self._gridManager.GetGrids(), self._players)
        self._view.DrawPlayerGetScore(self._players[self._current_player_index], score)

    def _adjustPlayerSequence(self):
        self._current_player_index += 1
        if self._current_player_index == len(self._players):
            self._current_player_index = 0

    def Run(self):
        self._join(Player("Player1"))
        self._join(Computer("Computer"))
        while not self._state == Game.EndGame:
            self._view.DrawCurrentPlayer(self._players[self._current_player_index])
            if self._state == Game.Playing and self._players[self._current_player_index].IsComputer():
                action, position = self._players[self._current_player_index].GetComputerAction(
                    self._gridManager.GetGrids())
            else:
                action, position = self._view.GePlayerActionPosition()

            if action == View.Quit:
                self._view.CloseWindows()
                self._state = Game.EndGame
                continue
            elif action == View.Replay:
                self._initGame(self._width, self._height)
                continue

            if self._state == Game.WaitingReplay:
                continue

            if action == View.Flag or action == View.ClickGrid:
                self._processPlayerAction(action, position)
