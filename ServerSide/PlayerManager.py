from Player import Player
from PlayerDAOFile import PlayerDAOFile


class PlayerManager(object):
    def __init__(self):
        self._dao = PlayerDAOFile()

    def GetPlayerInfo(self, name):
        playerInfo = self._dao.FindByName(name)
        return None if playerInfo is None else Player(playerInfo["Name"])

    def Create(self, name):
        player = self._dao.FindByName(name)
        if player is not None:
            return False

        self._dao.Insert(name)
        return True
