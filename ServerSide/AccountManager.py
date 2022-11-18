import jwt
from AccountDao import AccountDao
from Player import Player


class AccountManager(object):
    SECRET_KEY = "IGS"

    def __init__(self, registerFunc):
        self._dao = AccountDao()
        self._tokens = []
        registerFunc('Login', self._login, useAuth=False)
        registerFunc('Register', self._create, useAuth=False)

    def GetPlayerInfoByToken(self, token):
        info = self._decodeToken(token)
        if info is None:
            return None
        return self._getPlayerInfoByName(info['Name'])

    def IsValidToken(self, token):
        return self._decodeToken(token) is not None

    def _login(self, **kwargs):
        name, password = kwargs['Name'], kwargs['Password']
        account = self._dao.FindAccount(name)
        isSuccess = not (account is None or account["Password"] != password)
        if not isSuccess:
            return -110, None

        player = self._getPlayerInfoByName(name)
        return 0, {"Token": self._encodeToken(player.GetName())}

    def _create(self, **kwargs):
        name, password = kwargs['Name'], kwargs['Password']
        player = self._dao.FindAccount(name)
        if player is not None:
            return -109, None

        self._dao.CreateAccount(name, password)
        return 0, None

    def _getPlayerInfoByName(self, name):
        playerInfo = self._dao.FindAccount(name)
        return None if playerInfo is None else Player(playerInfo["Name"])

    def _encodeToken(self, name):
        token = jwt.encode({
            "Name": name,
        }, AccountManager.SECRET_KEY)
        self._tokens.append(token)
        return token

    def _decodeToken(self, token):
        try:
            if token not in self._tokens:
                return None
            return jwt.decode(token, key=AccountManager.SECRET_KEY)
        except:
            return None

