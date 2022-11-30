from redis.client import Redis
from DbDao import DbDao


class AccountDao(object):

    def __init__(self, expireSec):
        # self._dao = FileDao("Players", "json")
        self._dao = DbDao("Minesweeper", "Players")
        self._redis = Redis("localhost", 6379, decode_responses=True)
        self._expireSec = expireSec

    def CreateAccount(self, name, password):
        data = {
            "Name": name,
            "Password": password
        }
        return self._dao.Insert(name, data)

    def FindAccount(self, name):
        return self._dao.Find(name)

    def GetToken(self, name):
        return self._redis.get(name)

    def SetToken(self, name, token):
        return self._redis.set(name, token, ex=self._expireSec)

    def RefreshExpireTime(self, name):
        return self._redis.expire(name, self._expireSec)
