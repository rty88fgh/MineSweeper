import jwt
from AccountDao import AccountDao
from Player import Player


class AccountManager(object):
    SECRET_KEY = "IGS"

    def __init__(self, registerFunc):
        self._dao = AccountDao(6000)
        namespace = "Account"
        registerFunc('Login', self.OnLogin, useAuth=False, namespace=namespace)
        registerFunc('Register', self.OnCreate, useAuth=False, namespace=namespace)

    def GetPlayerInfoByToken(self, token):
        name = self._getName(token)
        return self.GetPlayerInfoByName(name) if name is not None else None

    def GetPlayerInfoByName(self, name):
        playerInfo = self._dao.FindAccount(name)
        return None if playerInfo is None else Player(playerInfo["Name"])

    def IsValidToken(self, token):
        name = self._getName(token)
        return self._dao.GetToken(name) == token if name is not None else False

    def RefreshToken(self, token):
        name = self._getName(token)
        return self._dao.RefreshExpireTime(name) if name is not None else False

    def OnLogin(self, **kwargs):
        name, password = kwargs['Name'], kwargs['Password']
        account = self._dao.FindAccount(name)
        isSuccess = not (account is None or account["Password"] != password)
        if not isSuccess:
            return -110, None

        player = self.GetPlayerInfoByName(name)
        return 0, {"Token": self._encodeToken(player.GetName())}

    def OnCreate(self, **kwargs):
        name, password = kwargs['Name'], kwargs['Password']
        player = self._dao.FindAccount(name)
        if player is not None:
            return -109, None
        try:
            result = self._dao.CreateAccount(name, password)
            return 0 if result else -109, None
        except:
            return -111, None

    def _encodeToken(self, name):
        token = jwt.encode({
            "Name": name,
        }, AccountManager.SECRET_KEY)
        self._dao.SetToken(name, token)
        return token

    def _getName(self, token):
        try:
            info = jwt.decode(token, key=AccountManager.SECRET_KEY)
        except:
            return None

        return info.get("Name") if info is not None else None

