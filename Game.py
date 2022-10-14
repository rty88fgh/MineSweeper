import copy

from Computer import Computer
from GridManager import GridManager
from Player import Player
from View import View


class Game(object):
    STATE = ["Init", "InitGrid", "WaitingPlayer", "Playing", "WaitingReplay", "EndGame"]

    def _setState(self, toState, fromState=None):
        if fromState is None:
            fromState = self._getState()

        if toState not in Game.STATE or fromState not in Game.STATE:
            return
        if not ((toState == self._getSTATE("InitGrid") and fromState == self._getSTATE("Init")) or
                (toState == self._getSTATE("WaitingPlayer") and fromState == self._getSTATE("InitGrid")) or
                (toState == self._getSTATE("Playing") and fromState == self._getSTATE("WaitingPlayer")) or
                (toState == self._getSTATE("WaitingReplay") and fromState == self._getSTATE("Playing")) or
                (toState == self._getSTATE("EndGame") and fromState == self._getSTATE("WaitingReplay")) or
                (toState == self._getSTATE("WaitingReplay") and fromState == self._getSTATE("InitGrid"))):
            return
        self._state = toState

    def _getState(self):
        return self._state

    def _getSTATE(self, value):
        return Game.STATE[Game.STATE.index(value)] if value in Game.STATE else None

    def __init__(self, width, height, mine_count):
        self._players = []
        self._gridManager = None
        self._view = None
        self._state = Game.STATE[0]
        self._current_player_index = 0
        self._mine_count = mine_count
        self._initGame(width, height)

    def Join(self, player):
        self._players.append(player)

    def _initGame(self, width, height):
        self._width = width
        self._height = height
        self._setState(self._getSTATE("InitGrid"))
        self._view = View(self._width, self._height)
        self._gridManager = GridManager(self._width, self._height, self._mine_count)
        self._setState(self._getSTATE("WaitingPlayer"))
        for player in self._players:
            player.ResetScore()
        self._current_player_index = 0
        self._view.RefreshView(self._gridManager.GetGrids(), self._players)

    def _processPlayerAction(self, action, position):
        if not self._gridManager._isValidGrid(position):
            return
        if action == View.ClickGrid:
            score = self._gridManager.RevealGrid(position)
        elif action == View.Flag:
            score = self._gridManager.MarkGrid(position)
        else:
            return

        self._addPlayerScore(score)
        self._adjustPlayerSeq()

        if self._gridManager.IsAllGridsClicked():
            order_players = [copy.copy(p) for p in self._players]
            order_players.sort(key=lambda player: player.GetScore(), reverse=True)
            self._view.DrawWin(order_players[0].GetName())
            self._setState(self._getSTATE("WaitingReplay"))

    def _addPlayerScore(self, score):
        if score < 0:
            self._players[self._current_player_index].SubScore(abs(score))
        else:
            self._players[self._current_player_index].AddScore(abs(score))

        self._view.RefreshView(self._gridManager.GetGrids(), self._players)
        self._view.DrawPlayerGetScore(self._players[self._current_player_index], score)

    def _adjustPlayerSeq(self):
        self._current_player_index += 1
        if self._current_player_index == len(self._players):
            self._current_player_index = 0

    def Run(self):
        # getState
        self._setState(self._getSTATE("Playing"))
        while not self._getState() == self._getSTATE("EndGame"):
            self._view.DrawCurrentPlayer(self._players[self._current_player_index])

            if self._getState() == self._getSTATE("Playing") and \
                    self._players[self._current_player_index].IsComputer():
                action, position = self._players[self._current_player_index].GetComputerActionPosition(
                    self._gridManager.GetGrids(), self._gridManager.GetAdjacentGrids)
            else:
                action, position = self._view.GePlayerActionPosition()

            if action == View.Quit:
                self._view.CloseWindows()
                self._setState(Game.STATE[4])
                continue
            elif action == View.Replay:
                self._initGame(self._width, self._height)
                self._setState(self._getSTATE("Playing"))
                continue

            if self._getState() == self._getSTATE("WaitingReplay"):
                continue

            if action == View.Flag or action == View.ClickGrid:
                self._processPlayerAction(action, position)

    def EndGame(self):
        self._view.CloseWindows()
        self._setState(self._getSTATE("EndGame"))
