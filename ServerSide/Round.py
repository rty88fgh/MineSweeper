import copy
import threading
import time
import gevent
from Computer import Computer
from GridContainer import GridContainer


class Round(object):
    STATE = ["Init", "Playing", "End"]

    def __init__(self, width, height, mineCount, playerCount, computerCount, roundId):
        self._computerThread = None
        self._players = []
        self._gridContainer = None
        self._state = Round.STATE[0]
        self._currentPlayer = 0
        self._mineCount = mineCount
        self._width = width
        self._height = height
        self._scoreMsg = {}
        self._lastUpdateTime = 0
        self._playerCount = playerCount
        self._computerCount = computerCount
        self._winner = None
        self._surrenders = []
        self._roundId = roundId

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

    def GetRoundId(self):
        return self._roundId

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

        if not self._gridContainer.IsValidGrid(position):
            return -107

        if str(action) == "OpenGrid":
            score = self._gridContainer.RevealGrid(position)
        elif str(action) == "SetFlagGrid":
            score = self._gridContainer.MarkGrid(position)
        else:
            return -108

        self._addPlayerScore(score)
        self._adjustPlayerSeq()

        if self._gridContainer.IsAllGridsClicked():
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
            "Grids": None if self.GetState() == "Init" else self._gridContainer.GetGrids().values(),
            "Players": [p.Serialize() for p in self._players],
            "Current": None if self.GetState() != "Playing" else self._players[self._currentPlayer].Serialize(),
            "ScoreMsg": scoreMsg,
            "Width": self._width,
            "Height": self._height,
            "State": self.GetState(),
            "Winner": winner,
            "LastUpdateTime": self._lastUpdateTime,
            "PlayerCount": self._playerCount,
            "ComputerCount": self._computerCount,
            "MineCount": self._mineCount,
            "RoundId": self.GetRoundId()
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

    @staticmethod
    def Restore(info, players):
        if info is None or players is None:
            return None

        width = info["Width"]
        height = info["Height"]
        mineCount = info["MineCount"]
        playerCount = info["PlayerCount"]
        computerCount = info["ComputerCount"]

        r = Round(width, height, mineCount, playerCount, computerCount)
        r._players = players
        r._winner = info["Winner"]
        r._state = info["State"]
        r._lastUpdateTime = info["LastUpdateTime"]

        if len(info["ScoreMsg"]) > 0:
            for i in range(len(info["ScoreMsg"])):
                r._scoreMsg[i] = info["ScoreMsg"][i]

        if r.GetState() != "Init":
            r._gridContainer = GridContainer.Restore(width, height, mineCount, info["Grids"])

        for p in [p for p in r._players]:
            p.Deserialize(**next(pInfo for pInfo in info["Players"] if pInfo["Name"] == p.GetName()))

            if p.IsComputer():
                p.SetGridContainer(r._gridContainer)

            if info["Current"] is not None and p.GetName() == info["Current"]["Name"]:
                r._currentPlayer = r._players.index(p)
        if r.GetState() == "Playing":
            r._setupComputer()

        return r

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
        self._gridContainer = GridContainer(self._width, self._height, self._mineCount)
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
            if self.GetState() != "Playing":
                break
            computerInfo = self._players[self._currentPlayer]
            action, pos = computerInfo.ProcessAction()
            self.ProcessPlayerAction(computerInfo, action, pos)
        self._computerThread = None

    def _setupComputer(self):
        if self._computerCount == 0:
            return

        num = 0
        while len([p for p in self._players if p.IsComputer()]) < self._computerCount:
            self._players.append(Computer("Computer{}".format(str(num)), self._gridContainer))
            num += 1

        if self._computerThread is None:
            self._computerThread = threading.Thread(target=self._computerRun)
            self._computerThread.setDaemon(True)
            self._computerThread.start()
