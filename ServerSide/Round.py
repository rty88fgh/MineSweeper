import copy
import threading
import time
import gevent
from Computer import Computer
from GridContainer import GridContainer


class Round(object):
    STATE = ["Init", "Playing", "End"]

    def __init__(self, width, height, mineCount, playerCount, computerCount):
        self._computerThread = None
        self._players = []
        self._gridManager = None
        self._state = Round.STATE[0]
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

        if toState not in Round.STATE or fromState not in Round.STATE:
            return
        if not ((fromState == "Init" and toState == "Playing") or
                (fromState == "Playing" and toState == "End")):
            return
        self._state = toState

    def GetState(self):
        return self._state

    def GetPlayers(self):
        return [p for p in self._players]

    def Join(self, player):
        allPlayers = [p.GetName() for p in self._players]
        name = player.GetName()
        if self.GetState() != "Init" and name not in allPlayers:
            return -102

        if name in [p.GetName() for p in self._players]:
            return 100  # Join back

        self._players.append(player)
        if len(self._players) == self._playerCount:
            self._startGame()
        return 0

    def Leave(self, player):
        if self.GetState() != "Init":
            return -102

        self._players.remove(next((p for p in self._players if p.GetName() == player.GetName())))
        return 0

    def ProcessPlayerAction(self, player, action, position):
        if not self.GetState() == "Playing":
            return -103

        if not player.GetName() == self._players[self._currentPlayer].GetName():
            return -106

        if not self._gridManager.IsValidGrid(position):
            return -107

        if str(action) == "OpenGrid":
            score = self._gridManager.RevealGrid(position)
        elif str(action) == "SetFlagGrid":
            score = self._gridManager.MarkGrid(position)
        else:
            return -108

        self._addPlayerScore(score)
        self._adjustPlayerSeq()

        if self._gridManager.IsAllGridsClicked():
            self._setState("End")
            self._winner = next(p for p in sorted([copy.copy(p) for p in self._players],
                                                  key=lambda p: p.GetScore(),
                                                  reverse=True)).GetName()

        self._lastUpdateTime = time.time()
        return 0

    def GetInfo(self):
        scoreMsg = [p[1] for p in sorted(self._scoreMsg.items(), key=lambda pair: pair[0])]
        winner = self._winner if self.GetState() == "End" else None
        return {
            "Grids": None if self.GetState() == "Init" else self._gridManager.GetGrids().values(),
            "Players": [p.Serialize() for p in self._players],
            "Current": None if self.GetState() != "Playing" else self._players[self._currentPlayer].Serialize(),
            "ScoreMsg": scoreMsg,
            "Width": self._width,
            "Height": self._height,
            "Status": self.GetState(),
            "Winner": winner,
            "LastUpdateTime": self._lastUpdateTime
        }

    def Surrender(self, player):
        name = player.GetName()

        if self.GetState() != "Playing":
            return -103

        self._surrenders.append(player)
        self._scoreMsg[len(self._scoreMsg)] = "{} surrender".format(name)
        self._adjustPlayerSeq()
        if len(self._players) - len(self._surrenders) <= 1:
            self._setState("End")
            lastPlayer = None
            if len(self._players) - len(self._surrenders) == 1:
                lastPlayer = ({p.GetName() for p in self._players} - {p.GetName() for p in self._surrenders}).pop()

            self._winner = "NoBody" if lastPlayer is None else lastPlayer

        self._lastUpdateTime = time.time()
        return 0

    def _addPlayerScore(self, score):
        player = self._players[self._currentPlayer]
        if score < 0:
            player.SubScore(abs(score))
        else:
            player.AddScore(abs(score))
        player_text = player.GetName() + " Score: " + ("+ " if score >= 0 else "- ") + str(abs(score))
        self._scoreMsg[len(self._scoreMsg)] = player_text

    def _adjustPlayerSeq(self):
        while len(self._players) - len(self._surrenders) > 0:
            self._currentPlayer = (self._currentPlayer + 1) % len(self._players)
            if self._players[self._currentPlayer].GetName() not in [p.GetName() for p in self._surrenders]:
                break

    def _startGame(self):
        self._gridManager = GridContainer(self._width, self._height, self.MineCount)
        for player in self._players:
            player.ResetScore()
        self._currentPlayer = 0
        self._scoreMsg = {}
        self._setupComputer()
        self._setState("Playing")
        self._lastUpdateTime = time.time()

    def _computerRun(self):
        while True:
            gevent.sleep(1)
            if not self._players[self._currentPlayer].IsComputer():
                continue
            if self.GetState() == "End":
                break
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
