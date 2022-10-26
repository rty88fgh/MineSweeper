import copy
import json
import threading
import time
import gevent
from Computer import Computer
from GridManager import GridManager
from PlayerManager import PlayerManager


class Game(object):
    STATE = ["Init", "InitGrid", "AdjustPlayer", "Playing", "WaitingReplay", "EndGame"]

    def __init__(self):
        self._initGame()
        self._computerThread = None
        self._playerManager = PlayerManager()
        self._mineCount = 0
        self._width = 0
        self._height = 0

    def _setState(self, toState, fromState=None):
        if fromState is None:
            fromState = self._getState()

        if toState not in Game.STATE or fromState not in Game.STATE:
            return
        if not ((fromState == "Init" and toState == "InitGrid") or
                (fromState == "InitGrid" and toState == "AdjustPlayer") or
                (fromState == "AdjustPlayer" and toState == "Playing") or
                (fromState == "Playing" and toState == "WaitingReplay") or
                (fromState == "WaitingReplay" and toState == "EndGame") or
                (fromState == "WaitingReplay" and toState == "InitGrid") or
                (fromState == "WaitingReplay" and toState == "Init") or
                (fromState == "Playing" and toState == "InitGrid")):
            return
        self._state = toState

    def _getState(self):
        return self._state

    def on_post_Join(self, req, resp):
        if not self._getState() == "Init":
            self._setRespMsg(resp, False, msg="It cannot join the player")
            return
        name = req.media.get("name", None)
        if name is None:
            resp.status = 400
            return

        if name in [p.GetName() for p in self._players]:
            self._setRespMsg(resp, True, msg="{} has joined the game.".format(name))
            return

        isSuccess = self._playerManager.IsLoginSuccess(name, req.media.get("pwd", None))
        if not isSuccess:
            resp.status = 401
            return

        player = self._playerManager.GetPlayerInfo(name)

        print "{} join the game".format(name)
        self._players.append(player)

        self._setRespMsg(resp, True, token="")

    def on_post_ConfigGame(self, req, resp):
        if not self._getState() in ["Init", "WaitingReplay"]:
            self._setRespMsg(resp, False, msg="It cannot config game")
            return

        try:
            self._mineCount = int(req.media["mineCount"])
            self._width = int(req.media["width"])
            self._height = int(req.media["height"])
            computerCount = int(req.media.get("computerCount", None))
            if computerCount is not None:
                for c in range(computerCount):
                    self._players.append(Computer("Computer{}".format(str(c))))
        except ValueError:
            self._setRespMsg(resp, False, msg="It is failed to convert type")

    def on_get_Start(self, req, resp):
        if not self._getState() in ["Init", "WaitingReplay"]:
            self._setRespMsg(resp, False, msg="It cannot start game")
            return
        if len(self._players) == 0:
            self._setRespMsg(resp, False, msg="The game must has one player")
            return
        self._startGame()
        self._setRespMsg(resp, True)

    def on_post_Action(self, req, resp):
        if not self._getState() == "Playing":
            self._setRespMsg(resp, False, msg="It cannot set click grid")
            return
        requestName = req.media.get("name", None)
        if not requestName == self._players[self._currentPlayer].GetName():
            self._setRespMsg(resp, False, msg="It is not {} turn".format(requestName))
            return

        x = req.media["x"]
        y = req.media["y"]
        action = req.media["action"]

        self._processPlayerAction(action, (x, y))

    def on_get_GameInfo(self, req, resp):
        scoreMsg = [p[1] for p in sorted(self._scoreMsg.items(), key=lambda pair: pair[0])]
        winner = self._winner if self._getState() == "WaitingReplay" else None
        resp.media = json.dumps({
            "grids": None if self._getState() == "Init" else self._gridManager.GetGrids().values(),
            "players": [p.Serialize() for p in self._players],
            "current": None if len(self._players) == 0 else self._players[self._currentPlayer].GetName(),
            "scoreMsg": scoreMsg,
            "status": self._state,
            "width": self._width,
            "height": self._height,
            "winner": None if winner is None else winner,
            "lastUpdateTime": self._lastUpdateTime
        })

    def on_post_Replay(self, req, resp):
        if not (self._getState() == "WaitingReplay" or
                self._getState() == "Playing"):
            self._setRespMsg(resp, False, msg="It cannot replay game")
            return
        self._startGame()

    def on_post_InitGame(self, req, resp):
        if self._getState() != "WaitingReplay":
            self._setRespMsg(resp, False, msg="It cannot init game")
            return

        print "Start to init game..."
        self._initGame()
        self._setRespMsg(resp, True)

    def on_post_Register(self, req, resp):
        name = req.media.get("name", None)
        if name is None:
            resp.status = 401
            return

        pwd = req.media.get("pwd", None)
        if pwd is None:
            self._setRespMsg(resp, False, "password can not be null")
            return

        isSuccess, msg = self._playerManager.Register(name, pwd)
        self._setRespMsg(resp, isSuccess, msg=msg)

    def _initGame(self):
        self._players = []
        self._gridManager = None
        self._state = Game.STATE[0]
        self._currentPlayer = 0
        self._mineCount = 0
        self._width = 0
        self._height = 0,
        self._scoreMsg = {}
        self._lastUpdateTime = 0

    def _processPlayerAction(self, action, position):
        if not self._gridManager.IsValidGrid(position):
            return
        if str(action) == "Click":
            score = self._gridManager.RevealGrid(position)
        elif str(action) == "Flag":
            score = self._gridManager.MarkGrid(position)
        else:
            return

        self._addPlayerScore(score)
        self._adjustPlayerSeq()

        if self._gridManager.IsAllGridsClicked():
            self._setState("WaitingReplay")
            self._winner = next(p for p in sorted([copy.copy(p) for p in self._players],
                                                  key=lambda player: player.GetScore(),
                                                  reverse=True)).GetName()

        self._lastUpdateTime = time.time()

    def _addPlayerScore(self, score):
        player = self._players[self._currentPlayer]
        if score < 0:
            player.SubScore(abs(score))
        else:
            player.AddScore(abs(score))
        player_text = player.GetName() + " Score: " + ("+ " if score >= 0 else "- ") + str(abs(score))
        self._scoreMsg[len(self._scoreMsg)] = player_text

    def _adjustPlayerSeq(self):
        self._currentPlayer = (self._currentPlayer + 1) % len(self._players)

    def _setRespMsg(self, resp, isSuccess, msg="", status=200, **kwargs):
        resp.status = status
        resp.headers["Content-type"] = "application/json"
        rtn = {
            "isSuccess": isSuccess,
            "message": msg
        }
        for k, v in kwargs.items():
            rtn[k] = v

        resp.media = json.dumps(rtn)
        if len(msg) != 0:
            print msg

    def _startGame(self):
        self._setState("InitGrid")
        self._gridManager = GridManager(self._width, self._height, self._mineCount)
        self._setState("AdjustPlayer")
        for player in self._players:
            player.ResetScore()
        self._currentPlayer = 0
        self._setState("Playing")
        self._lastUpdateTime = time.time()
        self._scoreMsg = {}
        if self._computerThread is None:
            self._computerThread = threading.Thread(target=self._computerRun)
            self._computerThread.setDaemon(True)
            self._computerThread.start()

    def _computerRun(self):
        while self._state not in ["Init", "EndGame"]:
            gevent.sleep(1)
            if self._state != "Playing":
                continue
            if not self._players[self._currentPlayer].IsComputer():
                continue
            action, pos = self._players[self._currentPlayer].GetActPos(self._gridManager.GetGrids(),
                                                                       self._gridManager.GetAdjacentGrids)
            self._processPlayerAction(action, pos)
        self._computerThread = None
