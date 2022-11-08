import json
from Game import Game
from PlayerManager import PlayerManager


class GameManager(object):
    def __init__(self):
        self._playerManager = PlayerManager()
        self._allGames = []
        self._allPlayers = {}

    def on_post_Login(self, req, resp):
        name = req.media.get("Name", None)
        if name is None:
            resp.status = 400
            return

        isSuccess, token = self._playerManager.IsLoginSuccess(name, req.media.get("Pwd", None))
        if not isSuccess:
            resp.status = 401
            return

        self._setRespMsg(resp, True, Token=token)

    def on_post_JoinGame(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)
        if not isValid:
            return

        name = player.GetName()
        if name in self._allPlayers and self._allPlayers[name].GetStatus() != "End":
            self._setRespMsg(resp, True, msg="{} has been join game".format(name))
            return

        gameIndex = req.media.get("id", None)
        if gameIndex is None:
            resp.status = 400
            return

        if len(self._allGames) < gameIndex:
            self._setRespMsg(resp, False, msg="Failed to find game id")
            return

        game = self._allGames[gameIndex]
        isSuccess, msg = game.Join(player)
        if isSuccess:
            self._allPlayers[name] = game
        self._setRespMsg(resp, isSuccess, msg=msg)

    def on_get_GetAllGamesInfo(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)
        if not isValid:
            return
        result = []
        for game in [g for g in self._allGames if g.GetState() != "End"]:
            info = game.GetGameInfo()
            result.append({
                "Players": [p.GetName() for p in info["Players"]],
                "Status": info["Status"],
                "GameId": self._allGames.index(game)
            })

        resp.media = result

    def on_post_CreateNewGame(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)
        if not isValid:
            return
        name = player.GetName()
        if name in self._allPlayers and self._allPlayers[name].GetState() != "End":
            self._setRespMsg(resp,
                             False,
                             msg=" Failed to create new game. {} has been join game.".format(name))
            return

        try:
            mineCount = int(req.media["MineCount"])
            width = int(req.media["Width"])
            height = int(req.media["Height"])
            playerCount = int(req.media["PlayerCount"])
            computerCount = int(req.media.get("ComputerCount", None))

            isSuccess, msg = True, None
            if width < 5 or width > 20:
                isSuccess, msg = False, "Width must be 5 ~ 20"
            elif height < 5 or height > 20:
                isSuccess, msg = False, "Height must be 5 ~ 20"
            elif mineCount < 1 or mineCount > 20:
                isSuccess, msg = False, "mineCount must be 5 ~ 20"
            elif playerCount < 1:
                isSuccess, msg = False, "playerCount must greater then 1"
            elif computerCount < 0:
                isSuccess, msg = False, "computerCount must greater then 0"

            if isSuccess:
                game = Game(width, height, mineCount, playerCount, computerCount)
                game.Join(player)
                self._allGames.append(game)
                self._allPlayers[player.GetName()] = game

            self._setRespMsg(resp, isSuccess, msg=msg, GameId=self._allGames.index(game) if isSuccess else None)
        except ValueError:
            self._setRespMsg(resp, False, msg="It is failed to convert type")

    def on_post_Click(self, req, resp):
        self._processPlayerActionRequest(req, resp, "Click")

    def on_post_Flag(self, req, resp):
        self._processPlayerActionRequest(req, resp, "Flag")

    def on_get_GetGameDetail(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)
        if not isValid:
            return

        if player.GetName() not in self._allPlayers:
            self._setRespMsg(resp, False, msg="{} did not join games".format(player.GetName()))
            return

        game = self._allPlayers[player.GetName()]
        info = game.GetGameInfo()
        info["Players"] = [p.Serialize() for p in info["Players"]]
        info["Current"] = None if info["Current"] is None else info["Current"].Serialize()
        resp.media = info

    def on_post_Surrender(self, req, resp):
        isValid, player = self._isValidPlayer(req, resp)
        if not isValid:
            return

        if player.GetName() not in self._allPlayers:
            self._setRespMsg(resp, False, msg="{} did not join games")
            return

        game = self._allPlayers[player.GetName()]
        isSuccess, msg = game.Surrender(player)
        self._setRespMsg(resp, isSuccess, msg=msg)

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

    def _processPlayerActionRequest(self, req, resp, action):
        isValid, player = self._isValidPlayer(req, resp)
        if not isValid:
            return

        if player.GetName() not in self._allPlayers:
            self._setRespMsg(resp, False, msg="{} did not join games")
            return

        position, msg = self._getPosition(req)
        if position is None:
            self._setRespMsg(resp, False, msg=msg)
            return

        game = self._allPlayers[player.GetName()]
        isSuccess, msg = game.ProcessPlayerAction(player, action, position)
        self._setRespMsg(resp, isSuccess, msg=msg)

    def _setRespMsg(self, resp, isSuccess, msg=None, status=200, **kwargs):
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

        player = self._playerManager.GetPlayerInfo(playerName)
        if player is None:
            resp.status = 401
            return False, None

        return True, player

    def _getPosition(self, req):
        x = req.media.get("X", None)
        y = req.media.get("Y", None)
        if x is None or y is None:
            return None, "Please enter x and y"

        return (x, y), None
