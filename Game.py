import copy

from Computer import Computer
from GridManager import GridManager
from Player import Player
from Rule import Rule
from View import View


class Game(object):
    StateMap = {
        "InitGrid": "InitGrid",
        "WaitingPlayer": "WaitingPlayer",
        "Playing": "Playing",
        "WaitingReplay": "WaitingReplay",
        "EndGame": "EndGame",
    }

    def __init__(self, width, height, mine_count):
        self._players = []
        self._gridManager = None
        self._view = None
        self._state = Game.StateMap["InitGrid"]
        self._current_player_index = 0
        self._rule = Rule()
        self._width = width
        self._height = height
        self._mine_count = mine_count

    def Join(self, player):
        self._players.append(player)

    def Run(self):
        self.Join(Player("Player1"))
        self.Join(Computer("Computer"))
        self.InitGame()
        while not self._state == Game.StateMap["EndGame"]:
            self._view.DrawCurrentPlayer(self._players[self._current_player_index])
            if self._state == Game.StateMap["Playing"] and self._players[self._current_player_index].GetIsComputer():
                action, position = self._players[self._current_player_index].ComputerAction()
            else:
                action, position = self._view.GePlayerActionPosition()

            if action == View.PlayerAction["Quit"]:
                self._view.EndGame()
                self._state = Game.StateMap["EndGame"]
                continue
            elif action == View.PlayerAction["Replay"]:
                self.InitGame()
                continue

            if self._state == Game.StateMap["WaitingReplay"]:
                continue

            if action == View.PlayerAction["Flag"] or action == View.PlayerAction["ClickGrid"]:
                self.ProcessGridAndCalculateScore(action, position)

    def InitGame(self):
        self._state = Game.StateMap["InitGrid"]
        self._view = View(self._width, self._height)
        manager = GridManager(self._width, self._height, self._mine_count)
        manager.InitGrids()
        self._gridManager = manager
        # setup players
        for player in self._players:
            player.ResetScore()
            if player.GetIsComputer():
                player.SetGridContainer(self._gridManager)

        self._view.RefreshView(manager.GetGrids(), self._players)
        self._state = Game.StateMap["Playing"]
        self._current_player_index = 0

    def ProcessGridAndCalculateScore(self, action, position):
        touch_grids = None
        if action == View.PlayerAction["ClickGrid"]:
            touch_grids = self._gridManager.RevealGrid(position)
        elif action == View.PlayerAction["Flag"]:
            touch_grids = self._gridManager.Mark(position)

        score = Rule.CalculateScore(touch_grids, action == View.PlayerAction["ClickGrid"])

        if score == 0:
            return

        self.AddPlayerScore(score)
        self.AdjustPlayerSequence()

        if self._gridManager.IsAllGridsClicked():
            order_players = [copy.copy(p) for p in self._players]
            order_players.sort(key=lambda player: player.GetScore(), reverse=True)
            self._view.DrawWin(order_players[0].GetName())
            self._state = Game.StateMap["WaitingReplay"]

    def AddPlayerScore(self, score):
        self._players[self._current_player_index].AddScore(score)
        self._view.RefreshView(self._gridManager.GetGrids(), self._players)
        self._view.DrawPlayerGetScore(self._players[self._current_player_index], score)

    def AdjustPlayerSequence(self):
        self._current_player_index += 1
        if self._current_player_index == len(self._players):
            self._current_player_index = 0
