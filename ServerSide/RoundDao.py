import datetime

import pymongo

from DbDao import DbDao


class RoundDao(object):

    def __init__(self):
        self._dao = DbDao("Minesweeper", "Round")

    def LogRoundInfo(self, roundInfo, roundId):
        roundInfo["RoundId"] = roundId
        return self._dao.Insert(roundInfo)

    def GetLastRoundId(self):
        return self._dao.Find({},
                              sort=[("RoundId", -1)],
                              projection={
                                  "RoundId": True,
                                  "_id": False,
                              }).get("RoundId", None)

    def LogAction(self, player, roundId, action, position, roundInfo, code, **kwargs):
        log = {
            "Name": player.GetName(),
            "RoundId": roundId,
            "Action": action,
            "Position": position,
            "RoundInfo": roundInfo,
            "CreateTime": datetime.datetime.now(),
            "Code": code,
        }
        if kwargs is not None:
            log.update(kwargs)

        return self._dao.Insert(log, collection="Log")
