import json
import jwt
import hashlib

from Player import Player


class PlayerManager(object):
    PLAYER_INFO_FILE = "PlayerInfo.json"
    SECRET_KEY = "IGS"

    def __init__(self):
        self._tokens = []

    def GetPlayerInfo(self, name):
        players = json.load(open(PlayerManager.PLAYER_INFO_FILE, "r"))
        info = next((p for p in players if p["Name"] == name), None)
        return Player(info["Name"]) if info is not None else None

    def IsLoginSuccess(self, name, pwd):
        players = json.load(open(PlayerManager.PLAYER_INFO_FILE, "r"))
        info = next((p for p in players if p["Name"] == name), None)
        hashAlgo = hashlib.md5()
        hashAlgo.update(pwd)
        hashPwd = hashAlgo.hexdigest()
        if info is None or info["Pwd"] != hashPwd:
            return False, None

        token = jwt.encode({
            "Name": name,
        }, PlayerManager.SECRET_KEY)
        self._tokens.append(token)
        return True, token

    def Register(self, name, pwd):
        players = json.load(open(PlayerManager.PLAYER_INFO_FILE, "r"))
        player = self.GetPlayerInfo(name)
        if player is not None:
            return False, "{} is duplicate".format(name)
        self._hashAlgo.update(pwd)
        players.append({
            "Name": name,
            "Pwd": self._hashAlgo.hexdigest()
        })
        fp = open(PlayerManager.PLAYER_INFO_FILE, "w+")
        fp.write(json.dumps(players))

        return True, None

    def VerifyToken(self, token):
        try:
            if token not in self._tokens:
                return None
            return jwt.decode(token, key=PlayerManager.SECRET_KEY)
        except:
            return None
