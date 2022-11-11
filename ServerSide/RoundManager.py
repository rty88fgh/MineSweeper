import json

from Code import Code
from Round import Game
from PlayerManager import PlayerManager


class RoundManager(object):
    def __init__(self):
        self._nextRoundId = 1
        self._playerManager = PlayerManager()
        self._allGames = {}
        self._allPlayers = {}

    def JoinRound(self, player, roundId):
        name = player.GetName()
        if roundId not in self._allGames:
            return Code.ROUNDID_NOT_FIND

        if name in self._allPlayers and \
                self._allPlayers[name] != self._allGames[roundId] and \
                self._allPlayers[name].GetState() != "End":
            return Code.HAVE_JOINED

        game = self._allGames[roundId]
        code = game.Join(player)
        if code >= 0:
            self._allPlayers[name] = game
        return code

    def LeaveRound(self, player):
        name = player.GetName()
        if name not in self._allPlayers:
            return Code.PLAYER_NOT_JOIN

        game = self._allPlayers[name]
        code = game.Leave(player)
        if code >= 0:
            del self._allPlayers[name]
        return code

    def GetAllRound(self):
        result = []
        for roundId, game in [(k, v) for k, v in self._allGames.items() if v.GetState() != "End"]:
            info = game.GetInfo()
            info["RoundId"] = roundId
            result.append(info)

        return result

    def CreateRound(self, player, mineCount, width, height, playerCount, computerCount):
        name = player.GetName()
        if name in self._allPlayers and self._allPlayers[name].GetState() != "End":
            return Code.HAVE_JOINED, None

        if width < 5 or width > 20 or \
                height < 5 or height > 20 or \
                mineCount < 1 or mineCount > 20 or \
                playerCount < 1 or \
                computerCount < 0:
            return Code.PARAMS_INVALID, None
        game = Game(width, height, mineCount, playerCount, computerCount)
        game.Join(player)
        roundId = self._nextRoundId
        self._nextRoundId += 1
        self._allGames[roundId] = game
        self._allPlayers[player.GetName()] = game
        return Code.SUCCESS, roundId

    def ProcessAction(self, player, action, position):
        if player.GetName() not in self._allPlayers:
            return Code.PLAYER_NOT_JOIN

        game = self._allPlayers[player.GetName()]
        return game.ProcessPlayerAction(player, action, position)

    def GetJoinedRound(self, player):
        if player.GetName() not in self._allPlayers:
            return None

        game = self._allPlayers[player.GetName()]
        return game.GetInfo()

    def Surrender(self, player):
        if player.GetName() not in self._allPlayers:
            return Code.PLAYER_NOT_JOIN

        game = self._allPlayers[player.GetName()]
        return game.Surrender(player)

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





