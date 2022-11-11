import json
from hashlib import md5

from AccountManager import AccountManager
from Code import Code
from RoundManager import RoundManager
from PlayerManager import PlayerManager


class Dispatcher(object):
    def __init__(self):
        self._accountManager = AccountManager()
        self._playerManager = PlayerManager()
        self._gameManager = RoundManager()

    def on_post_Login(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        name = req.media.get("Name", None)
        password = req.media.get("Password", None)
        if name is None or password is None:
            self._setRespMsg(resp, Code.PARAMS_INVALID)
            return

        isSuccess = self._accountManager.Login(name, password)
        if not isSuccess:
            self._setRespMsg(resp, Code.LOGIN_FAILED)
            return
        player = self._playerManager.GetPlayerInfo(name)
        token = self._accountManager.EncodeToken(player.GetName())
        self._setRespMsg(resp, Code.SUCCESS, Token=token)

    def on_post_Join(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        roundId = req.media.get("RoundId", None)
        if roundId is None:
            self._setRespMsg(resp, Code.PARAMS_INVALID)
            return
        player = self._playerManager.GetPlayerInfo(info["Name"])
        code = self._gameManager.JoinRound(player, roundId)
        self._setRespMsg(resp, code)

    def on_post_Leave(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        player = self._playerManager.GetPlayerInfo(info["Name"])
        code = self._gameManager.LeaveRound(player)
        self._setRespMsg(resp, code)

    def on_get_GetAllRound(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        allInfo = self._gameManager.GetAllRound()
        self._setRespMsg(resp, Code.SUCCESS, data=allInfo)

    def on_post_Create(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        try:
            mineCount = int(req.media["MineCount"])
            width = int(req.media["Width"])
            height = int(req.media["Height"])
            playerCount = int(req.media["PlayerCount"])
            computerCount = int(req.media.get("ComputerCount", None))
            player = self._playerManager.GetPlayerInfo(info["Name"])
            code, roundId = self._gameManager.CreateRound(player, mineCount, width, height, playerCount,
                                                          computerCount)
            self._setRespMsg(resp, code, RoundId=roundId)
        except ValueError:
            self._setRespMsg(resp, Code.PARAMS_ERROR)

    def on_post_Open(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        self._processPlayerAction(req, resp, "Open")

    def on_post_SetFlag(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        self._processPlayerAction(req, resp, "SetFlag")

    def on_get_GetJoinedRound(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        player = self._playerManager.GetPlayerInfo(info["Name"])
        roundInfo = self._gameManager.GetJoinedRound(player)

        if roundInfo is None:
            self._setRespMsg(resp, Code.PLAYER_NOT_JOIN)
        else:
            self._setRespMsg(resp, Code.SUCCESS, data=roundInfo)

    def on_post_Surrender(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        player = self._playerManager.GetPlayerInfo(info["Name"])

        code = self._gameManager.Surrender(player)
        self._setRespMsg(resp, code)

    def on_post_Register(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        name = req.media.get("Name", None)
        password = req.media.get("Password", None)
        if name is None or password is None:
            self._setRespMsg(resp, Code.PARAMS_INVALID)
            return

        if not self._playerManager.Create(name) or not self._accountManager.Create(name, password):
            return self._setRespMsg(resp, Code.PLAYER_DUPLICATE)
        self._setRespMsg(resp, Code.SUCCESS)

    def _getTokenInfo(self, req, resp):
        token = req.headers.get("Authorization".upper(), None)
        if token is None:
            resp.status = 401
            return None

        tokenInfo = self._accountManager.DecodeToken(token)
        if tokenInfo is None:
            resp.status = 401
            return None

        return tokenInfo

    def _setRespMsg(self, resp, code, status=200, **kwargs):
        resp.status = status
        resp.headers["Content-type"] = "application/json"
        rtn = {
            "Code": code,
        }
        for k, v in kwargs.items():
            rtn[k] = v

        resp.media = rtn
        if code < 0:
            print "Error Code:" + next((k for k, v in vars(Code).items() if v == code))

    def _getPosition(self, req):
        x = req.media.get("X", None)
        y = req.media.get("Y", None)
        return None if x is None or y is None else (x, y)

    def _processPlayerAction(self, req, resp, action):
        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        player = self._playerManager.GetPlayerInfo(info["Name"])
        position = self._getPosition(req)
        if position is None:
            self._setRespMsg(resp, Code.PARAMS_INVALID)
            return

        code = self._gameManager.ProcessAction(player, action, position)
        self._setRespMsg(resp, code)

    def _isValidRequest(self, req):
        checkSum = req.headers.get("CheckSum".upper(), None)
        if checkSum is None:
            return False

        keyStr = ""
        if req.media is not None:
            sortKey = [k for k in req.media.keys()]
            sortKey.sort(key=lambda key: key)
            for k in sortKey:
                keyStr += "{}={}&".format(k, req.media[k])

        hashAlgo = md5()
        hashAlgo.update(keyStr)
        return hashAlgo.hexdigest() == checkSum
