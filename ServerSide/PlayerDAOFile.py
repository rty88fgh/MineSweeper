import json

from DAOBase import DAOBase


class PlayerDAOFile(DAOBase):
    PLAYER_INFO_FILE = "PlayerInfo.json"

    def Insert(self, name):
        accounts = json.load(open(PlayerDAOFile.PLAYER_INFO_FILE, "r"))
        account = self.FindByName(name)
        if account is not None:
            return None

        account = {
            "Name": name,
        }
        accounts.append(account)
        fp = open(PlayerDAOFile.PLAYER_INFO_FILE, "w+")
        fp.write(json.dumps(accounts))
        return account

    def FindAll(self):
        return json.load(open(PlayerDAOFile.PLAYER_INFO_FILE, "r"))

    def FindByName(self, name):
        players = json.load(open(PlayerDAOFile.PLAYER_INFO_FILE, "r"))
        return next((p for p in players if p["Name"] == name), None)

    def DeleteByName(self, name):
        players = json.load(open(PlayerDAOFile.PLAYER_INFO_FILE, "r"))
        player = next((p for p in players if p["name"] == name), None)
        if player is None:
            return None

        del players[player]
        fp = open(PlayerDAOFile.PLAYER_INFO_FILE, "w+")
        fp.write(json.dumps(players))
        return player

