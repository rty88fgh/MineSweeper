import copy
import json
import threading
import time
import gevent
from Computer import Computer
from GridManager import GridManager
from PlayerManager import PlayerManager


class Game(object):
    STATE = ["Start", "InitGame", "Playing", "WaitingReplay", "End"]

    def __init__(self):
        self._initGame()
        self._computerThread = None
        self._playerManager = PlayerManager()
        self._mineCount = 0
        self._width = 0
        self._height = 0
        self._computerCount = 0

    def _setState(self, toState, fromState=None):
        if fromState is None:
            fromState = self._getState()

        if toState not in Game.STATE or fromState not in Game.STATE:
            return
        if not ((fromState == "Start" and toState == "InitGame") or
                (fromState == "InitGame" and toState == "Playing") or
                (fromState == "Playing" and toState == "WaitingReplay") or
                (fromState == "WaitingReplay" and toState == "End") or
                (fromState == "WaitingReplay" and toState == "InitGame") or
                (fromState == "WaitingReplay" and toState == "Start") or
                (fromState == "Playing" and toState == "InitGame")):
            return
        self._state = toState

    def _getState(self):
        return self._state

    def on_post_Login(self, req, resp):
        if self._getState() == "End":
            self._setRespMsg(resp, False, msg="Failed to Login. Game status: {}".format(self._getState()))
            return
        name = req.media.get("Name", None)
        if name is None:
            resp.status = 400
            return

        isSuccess, token = self._playerManager.IsLoginSuccess(name, req.media.get("Pwd", None))
        if not isSuccess:
            resp.status = 401
            return

        currentPlayers = [p.GetName() for p in self._players]
        if self._getState() != "Start" and name not in currentPlayers:
            self._setRespMsg(resp, False,
                             msg="The game has been started. Please init the game if you want to join game")
            return

        if name in [p.GetName() for p in self._players]:
            self._setRespMsg(resp, True, msg="{} has logon the game.".format(name), Token=token)
            return

        player = self._playerManager.GetPlayerInfo(name)

        print "{} join the game".format(name)
        self._players.append(player)

        self._setRespMsg(resp, True, Token=token)

    def on_post_ConfigGame(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)

        if not isValid:
            return

        if not self._getState() in ["Start", "WaitingReplay"]:
            self._setRespMsg(resp, False, msg="It cannot config game")
            return

        try:
            self._mineCount = int(req.media["MineCount"])
            self._width = int(req.media["Width"])
            self._height = int(req.media["Height"])
            self._computerCount = int(req.media.get("ComputerCount", None))
            self._setRespMsg(resp, True)
        except ValueError:
            self._setRespMsg(resp, False, msg="It is failed to convert type")

    def on_post_Start(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)

        if not isValid:
            return

        if not self._getState() in ["Start", "WaitingReplay"]:
            self._setRespMsg(resp, False, msg="It cannot start game")
            return
        if len(self._players) == 0:
            self._setRespMsg(resp, False, msg="The game must has one player")
            return
        self._startGame()
        self._setRespMsg(resp, True)

    def on_post_Click(self, req, resp):
        isValid, position = self._isValidPlayerAction(req, resp)
        if not isValid:
            return

        self._processPlayerAction("Click", position)
        self._setRespMsg(resp, True)

    def on_post_Flag(self, req, resp):
        isValid, position = self._isValidPlayerAction(req, resp)
        if not isValid:
            return

        self._processPlayerAction("Flag", position)
        self._setRespMsg(resp, True)

    def on_get_GetGameInfo(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)
        if not isValid:
            return

        scoreMsg = [p[1] for p in sorted(self._scoreMsg.items(), key=lambda pair: pair[0])]
        winner = self._winner if self._getState() == "WaitingReplay" else None
        resp.media = json.dumps({
            "Grids": None if self._getState() == "Start" else self._gridManager.GetGrids().values(),
            "Players": [p.Serialize() for p in self._players],
            "Current": None if len(self._players) == 0 else self._players[self._currentPlayer].GetName(),
            "ScoreMsg": scoreMsg,
            "Status": self._state,
            "Width": self._width,
            "Height": self._height,
            "Winner": None if winner is None else winner,
            "LastUpdateTime": self._lastUpdateTime
        })

    def on_post_Replay(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)

        if not isValid:
            return

        if not (self._getState() == "WaitingReplay" or
                self._getState() == "Playing"):
            self._setRespMsg(resp, False, msg="It cannot replay game")
            return
        self._startGame()
        self._setRespMsg(resp, True)

    def on_post_InitGame(self, req, resp):
        if self._getState() != "WaitingReplay":
            self._setRespMsg(resp, False, msg="It cannot init game")
            return

        print "Start to init game..."
        self._initGame()
        self._setRespMsg(resp, True)

    def on_post_Register(self, req, resp):
        name = req.media.get("Name", None)
        if name is None:
            resp.status = 401
            return

        pwd = req.media.get("Pwd", None)
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

    def _isValidPlayerAction(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)

        if not isValid:
            return False, None

        if not self._getState() == "Playing":
            self._setRespMsg(resp, False, msg="It cannot set click grid")
            return False, None

        if not player == self._players[self._currentPlayer].GetName():
            self._setRespMsg(resp, False, msg="It is not {} turn".format(player))
            return False, None

        x = req.media.get("X", None)
        y = req.media.get("Y", None)
        if x is None or y is None:
            self._setRespMsg(resp, False, msg="Please enter x and y")
            return False, None

        return True, (x, y)

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
            "IsSuccess": isSuccess,
            "Message": msg
        }
        for k, v in kwargs.items():
            rtn[k] = v

        resp.media = rtn
        if msg is not None and len(msg) != 0:
            print msg

    def _startGame(self):
        self._setState("InitGame")
        self._gridManager = GridManager(self._width, self._height, self._mineCount)
        for player in self._players:
            player.ResetScore()
        self._currentPlayer = 0
        self._setState("Playing")
        self._lastUpdateTime = time.time()
        self._scoreMsg = {}
        self._setupComputer()

    def _computerRun(self):
        while self._state not in ["Start", "End"]:
            gevent.sleep(1)
            if self._state != "Playing":
                continue
            if not self._players[self._currentPlayer].IsComputer():
                continue
            action, pos = self._players[self._currentPlayer].ProcessAction()
            self._processPlayerAction(action, pos)
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

    def _isValidPlayer(self, req, resp):
        token = req.headers.get("Authorization".upper(), None)
        if token is None:
            resp.status = 401
            return False, None

        tokenInfo = self._playerManager.VerifyToken(token)
        if tokenInfo is None:
            resp.status = 401
            return False, None

        playerName = tokenInfo.get("Name", None)
        if playerName is None:
            resp.status = 401
            return False, None
        if playerName not in [p.GetName() for p in self._players]:
            resp.status = 401
            return False, None

        return True, playerName
