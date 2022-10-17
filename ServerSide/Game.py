import copy
import json
import time

import falcon

from GridManager import GridManager
from Player import Player


class Game(object):
    STATE = ["Init", "InitGrid", "AdjustPlayer", "Playing", "WaitingReplay", "EndGame"]
    ACTION = ["Click", "Flag"]
    PlayerInfoFile = "PlayerInfo.json"

    def __init__(self):
        self._players = []
        self._gridManager = None
        self._state = Game.STATE[0]
        self._currentPlayer = 0
        self._mineCount = 0
        self._width = 0
        self._height = 0,
        self._scoreMsg = {}
        self._lastUpdateTime = 0

    def _setState(self, toState, fromState=None):
        if fromState is None:
            fromState = self._getState()

        if toState not in Game.STATE or fromState not in Game.STATE:
            return
        if not ((fromState == self._getSTATE("Init") and toState == self._getSTATE("InitGrid")) or
                (fromState == self._getSTATE("InitGrid") and toState == self._getSTATE("AdjustPlayer")) or
                (fromState == self._getSTATE("AdjustPlayer") and toState == self._getSTATE("Playing")) or
                (fromState == self._getSTATE("Playing") and toState == self._getSTATE("WaitingReplay")) or
                (fromState == self._getSTATE("WaitingReplay") and toState == self._getSTATE("EndGame")) or
                (fromState == self._getSTATE("WaitingReplay") and toState == self._getSTATE("InitGrid")) or
                (fromState == self._getSTATE("Playing") and toState == self._getSTATE("InitGrid"))):
            return
        self._state = toState

    def _getState(self):
        return self._state

    def _getSTATE(self, value):
        return Game.STATE[Game.STATE.index(value)] if value in Game.STATE else None

    def _getACTION(self, value):
        return Game.ACTION[Game.ACTION.index(value)] if value in Game.ACTION else None

    def on_post_Join(self, req, resp):
        if not self._getState() == self._getSTATE("Init"):
            self._setRespMsg(resp, "It cannot join the player")
            return
        name = req.media.get("name", None)
        if name is None:
            raise falcon.HTTPNotFound()
        if name in [p.GetName() for p in self._players]:
            self._setRespMsg(resp, "{} has joined the game.".format(name))
            return

        player = self._getPlayer(name)
        if player is None:
            print "It is failed to read {} info".format(name)
            resp.status = 401
            return
        print "{} join the game".format(name)
        self._players.append(player)

        self._setRespMsg(resp)

    def _getPlayer(self, name):
        fp = open(Game.PlayerInfoFile, "r")
        text = fp.read()
        players = json.loads(text)
        return Player(next((p["name"] for p in players if p["name"] == name), None))

    def on_post_ConfigGame(self, req, resp):
        if not self._getState() in [self._getSTATE("Init"), self._getSTATE("WaitingReplay")]:
            self._setRespMsg(resp, "It cannot config game")
            return

        try:
            self._mineCount = int(req.media["mineCount"])
            self._width = int(req.media["width"])
            self._height = int(req.media["height"])
        except ValueError:
            self._setRespMsg(resp, "It is failed to convert type")

    def on_get_Start(self, req, resp):
        if not self._getState() in [self._getSTATE("Init"), self._getSTATE("WaitingReplay")]:
            self._setRespMsg(resp, "It cannot start game")
            return
        if len(self._players) == 0:
            resp.media = json.dumps({
                "isSuccess": False,
                "message": "The game must has one player"
            })
            return
        self._startGame()
        self._setRespMsg(resp)

    def on_post_Action(self, req, resp):
        if not self._getState() == self._getSTATE("Playing"):
            self._setRespMsg(resp, "It cannot set click grid")
            return
        requestName = req.media.get("name", None)
        if not requestName == self._players[self._currentPlayer].GetName():
            self._setRespMsg(resp, "It is not {} turn".format(requestName))
            return

        x = req.media["x"]
        y = req.media["y"]
        action = req.media["action"]

        self._processPlayerAction(action, (x, y))

    def on_get_GameInfo(self, req, resp):
        scoreMsg = [p[1] for p in sorted(self._scoreMsg.items(), key=lambda pair: pair[0])]
        winner = self._winner if self._getState() == self._getSTATE("WaitingReplay") else None
        resp.media = json.dumps({
            "grids": None if self._getState() == self._getSTATE("Init") else self._gridManager.GetGrids().values(),
            "players": [p.Serialize() for p in self._players],
            "current": self._players[self._currentPlayer].GetName(),
            "scoreMsg": scoreMsg,
            "status": self._state,
            "width": self._width,
            "height": self._height,
            "winner": None if winner is None else winner,
            "lastUpdateTime": self._lastUpdateTime
        })

    def on_post_Replay(self, req, resp):
        if not (self._getState() == self._getSTATE("WaitingReplay") or
                self._getState() == self._getSTATE("Playing")):
            self._setRespMsg(resp, "It cannot replay game")
            return
        self._startGame()

    def _processPlayerAction(self, action, position):
        if not self._gridManager.IsValidGrid(position):
            return
        if str(action) == self._getACTION("Click"):
            score = self._gridManager.RevealGrid(position)
        elif str(action) == self._getACTION("Flag"):
            score = self._gridManager.MarkGrid(position)
        else:
            return

        self._addPlayerScore(score)
        self._adjustPlayerSeq()

        if self._gridManager.IsAllGridsClicked():
            self._setState(self._getSTATE("WaitingReplay"))
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
        self._currentPlayer += 1
        if self._currentPlayer == len(self._players):
            self._currentPlayer = 0

    def _setRespMsg(self, resp, msg="", status=200):
        resp.status = status
        resp.headers["Content-type"] = "application/json"
        resp.media = json.dumps({
            "isSuccess": len(msg) == 0,
            "message": msg
        })
        if len(msg) != 0:
            print msg

    def _startGame(self):
        self._setState(self._getSTATE("InitGrid"))
        self._gridManager = GridManager(self._width, self._height, self._mineCount)
        self._setState(self._getSTATE("AdjustPlayer"))
        for player in self._players:
            player.ResetScore()
        self._currentPlayer = 0
        self._setState(self._getSTATE("Playing"))
        self._lastUpdateTime = time.time()
        self._scoreMsg = {}
