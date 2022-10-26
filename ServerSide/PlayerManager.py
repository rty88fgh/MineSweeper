import json

from Player import Player


class PlayerManager(object):
    PlayerInfoFile = "PlayerInfo.json"

    def GetPlayerInfo(self, name):
        players = json.load(open(PlayerManager.PlayerInfoFile, "r"))
        info = next((p for p in players if p["name"] == name), None)
        return Player(info["name"]) if info is not None else None

    def IsLoginSuccess(self, name, pwd):
        players = json.load(open(PlayerManager.PlayerInfoFile, "r"))
        info = next((p for p in players if p["name"] == name), None)
        return info["pwd"] == pwd if info is not None else False

    def Register(self, name, pwd):
        players = json.load(open(PlayerManager.PlayerInfoFile, "r"))
        player = self.GetPlayerInfo(name)
        if player is not None:
            return False, "{} is duplicate".format(name)

        players.append({
            "name": name,
            "pwd": pwd
        })
        fp = open(PlayerManager.PlayerInfoFile, "w+")
        fp.write(json.dumps(players))

        return True, None
