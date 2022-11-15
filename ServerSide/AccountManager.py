import hashlib

import jwt

from AccountDao import AccountDao
from ManagerBase import ManagerBase
from Player import Player


class AccountManager(ManagerBase):
    SECRET_KEY = "IGS"

    def __init__(self):
        super(AccountManager, self).__init__()
        self._dao = AccountDao()
        self._tokens = []
        self.RegisterProcessMethod('Login', 'Post', self._login, useAuth=False)
        self.RegisterProcessMethod('Register', 'Post', self._create, useAuth=False)

    def Process(self, **kwargs):
        funcName = kwargs['FuncName']
        return self.AllProcessMethod[funcName]['_func'](**kwargs)

    def GetPlayerInfoByToken(self, token):
        info = self._decodeToken(token)
        if info is None:
            return None
        return self._getPlayerInfoByName(info['Name'])

    def IsValidToken(self, token):
        return self._decodeToken(token) is not None

    def _login(self, **kwargs):
        name, password = kwargs['Name'], kwargs['Password']
        account = self._dao.FindByName(name)
        isSuccess = not (account is None or account["Password"] != password)
        if not isSuccess:
            return -110, None

        player = self._getPlayerInfoByName(name)
        return 0, {"Token": self._encodeToken(player.GetName())}

    def _create(self, **kwargs):
        name, password = kwargs['Name'], kwargs['Password']
        player = self._dao.FindByName(name)
        if player is not None:
            return -109, None

        self._dao.Insert(name, password)
        return 0, None

    def _getPlayerInfoByName(self, name):
        playerInfo = self._dao.FindByName(name)
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

