import copy
import json
import threading
import time
import gevent
from Computer import Computer
from GridManager import GridManager
from PlayerManager import PlayerManager


class Game(object):
    STATE = ["Init", "Playing", "End"]

    def __init__(self, width, height, mineCount, playerCount, computerCount):
        self._computerThread = None
        self._players = []
        self._gridManager = None
        self._state = Game.STATE[0]
        self._currentPlayer = 0
        self.MineCount = mineCount
        self._width = width
        self._height = height
        self._scoreMsg = {}
        self._lastUpdateTime = 0
        self._playerCount = playerCount
        self._computerCount = computerCount
        self._winner = None
        self._surrenders = []

    def _setState(self, toState, fromState=None):
        if fromState is None:
            fromState = self.GetState()

        if toState not in Game.STATE or fromState not in Game.STATE:
            return
        if not ((fromState == "Init" and toState == "Playing") or
                (fromState == "Playing" and toState == "End")):
            return
        self._state = toState

    def GetState(self):
        return self._state

    def Join(self, player):
        allPlayers = [p.GetName() for p in self._players]
        name = player.GetName()
        if self.GetState() != "Init" and name not in allPlayers:
            return False, "The game has been started."

        if name in [p.GetName() for p in self._players]:
            return True, "{} has logon the game.".format(name)

        self._players.append(player)
        if len(self._players) == self._playerCount:
            self._startGame()
        return True, None

    def Left(self, player):
        allPlayers = [p.GetName() for p in self._players]
        name = player.GetName()

        if name not in allPlayers:
            return False, "{} is not in the game".format(name)

        if self.GetState() != "Init":
            return False, "The game has been started. {} cannot left game.".format(name)

        self._players.remove(next((p for p in self._players if p.GetName() == player.GetName())))
        return True, None

    def ProcessPlayerAction(self, player, action, position):
        if not self.GetState() == "Playing":
            return False, "It cannot set click grid"

        if not player.GetName() == self._players[self._currentPlayer].GetName():
            return False, "It is not {} turn".format(player.GetName())

        if not self._gridManager.IsValidGrid(position):
            return False, "{} is not valid grid".format(position)
        if str(action) == "Click":
            score = self._gridManager.RevealGrid(position)
        elif str(action) == "Flag":
            score = self._gridManager.MarkGrid(position)
        else:
            return False, "{} is unknown action".format(action)

        self._addPlayerScore(score)
        self._adjustPlayerSeq()

        if self._gridManager.IsAllGridsClicked():
            self._setState("End")
            self._winner = next(p for p in sorted([copy.copy(p) for p in self._players],
                                                  key=lambda player: player.GetScore(),
                                                  reverse=True)).GetName()

        self._lastUpdateTime = time.time()
        return True, None

    def GetGameInfo(self):
        scoreMsg = [p[1] for p in sorted(self._scoreMsg.items(), key=lambda pair: pair[0])]
        winner = self._winner if self.GetState() == "End" else None
        return {
            "Grids": None if self.GetState() == "Init" else self._gridManager.GetGrids().values(),
            "Players": [p for p in self._players],
            "Current": None if self.GetState() != "Playing" else self._players[self._currentPlayer],
            "ScoreMsg": scoreMsg,
            "Width": self._width,
            "Height": self._height,
            "Status": self.GetState(),
            "Winner": winner,
            "LastUpdateTime": self._lastUpdateTime
        }

    def Surrender(self, player):
        name = player.GetName()
        if name not in [p.GetName() for p in self._players]:
            return False, "{} is not join game".format(name)
        if self.GetState() != "Playing":
            return False, "It cannot surrender while game status:{}".format(self.GetState())

        self._surrenders.append(player)
        self._scoreMsg[len(self._scoreMsg)] = "{} surrender".format(name)
        self._adjustPlayerSeq()
        if len(self._surrenders) == len(self._players) - 1:
            self._setState("End")
            self._winner = ({p.GetName() for p in self._players} -
                            {p.GetName() for p in self._surrenders}).pop()

        self._lastUpdateTime = time.time()
        return True, None

    def _addPlayerScore(self, score):
        player = self._players[self._currentPlayer]
        if score < 0:
            player.SubScore(abs(score))
        else:
            player.AddScore(abs(score))
        player_text = player.GetName() + " Score: " + ("+ " if score >= 0 else "- ") + str(abs(score))
        self._scoreMsg[len(self._scoreMsg)] = player_text

    def _adjustPlayerSeq(self):
        while True:
            self._currentPlayer = (self._currentPlayer + 1) % len(self._players)
            if self._players[self._currentPlayer].GetName() not in [p.GetName() for p in self._surrenders]:
                break

    def _startGame(self):
        self._gridManager = GridManager(self._width, self._height, self.MineCount)
        for player in self._players:
            player.ResetScore()
        self._currentPlayer = 0
        self._scoreMsg = {}
        self._setupComputer()
        self._setState("Playing")
        self._lastUpdateTime = time.time()

    def _computerRun(self):
        while self.GetState() != "End":
            gevent.sleep(1)
            if not self._players[self._currentPlayer].IsComputer():
                continue
            computerInfo = self._players[self._currentPlayer]
            action, pos = computerInfo.ProcessAction()
            self.ProcessPlayerAction(computerInfo, action, pos)
        self._computerThread = None

    def _setupComputer(self):
        if self._computerCount == 0:
            return

        self._players = [p for p in self._players if not p.IsComputer()]

        for c in range(self._computerCount):
            self._players.append(Computer("Computer{}".format(str(c)), self._gridManager))

        if self._computerThread is None:
            self._computerThread = threading.Thread(target=self._computerRun)
            self._computerThread.setDaemon(True)
            self._computerThread.start()
