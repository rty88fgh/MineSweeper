from hashlib import md5
from AccountManager import AccountManager
from RoundManager import RoundManager
# from PlayerManager import PlayerManager


class Dispatcher(object):
    def __init__(self):
        self._accountManager = AccountManager()
        # self._playerManager = PlayerManager()
        self._gameManager = RoundManager()

    def on_post_Login(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        name = req.media.get("Name")
        password = req.media.get("Password")
        if name is None or password is None:
            self._setRespMsg(resp, -105)
            return

        isSuccess = self._accountManager.Login(name, password)
        if not isSuccess:
            self._setRespMsg(resp, -110)
            return
        player = self._playerManager.GetPlayerInfo(name)
        token = self._accountManager.EncodeToken(player.GetName())
        self._setRespMsg(resp, 0, Token=token)

    def on_post_Join(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        roundId = req.media.get("RoundId")
        if roundId is None:
            self._setRespMsg(resp, -105)
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
        self._setRespMsg(resp, 0, data=allInfo)

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
            computerCount = int(req.media.get("ComputerCount"))
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

        self._processPlayerAction(req, resp, "OpenGrid")

    def on_post_SetFlag(self, req, resp):
        if not self._isValidRequest(req):
            resp.status = 401
            return

        self._processPlayerAction(req, resp, "SetFlagGrid")

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
            self._setRespMsg(resp, -104)
        else:
            self._setRespMsg(resp, 0, data=roundInfo)

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

        name = req.media.get("Name")
        password = req.media.get("Password")
        if name is None or password is None:
            self._setRespMsg(resp, -105)
            return

        if not self._playerManager.Create(name) or not self._accountManager.Create(name, password):
            return self._setRespMsg(resp, -109)
        self._setRespMsg(resp, 0)

    def _getTokenInfo(self, req, resp):
        token = req.headers.get("Authorization".upper())
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

    def _getPosition(self, req):
        x = req.media.get("X")
        y = req.media.get("Y")
        return None if x is None or y is None else (x, y)

    def _processPlayerAction(self, req, resp, action):
        info = self._getTokenInfo(req, resp)
        if info is None:
            return

        player = self._playerManager.GetPlayerInfo(info["Name"])
        position = self._getPosition(req)
        if position is None:
            self._setRespMsg(resp, -105)
            return

        code = self._gameManager.ProcessAction(player, action, position)
        self._setRespMsg(resp, code)

    def _isValidRequest(self, req):
        checkSum = req.headers.get("CheckSum".upper())
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
