import datetime

from DbDao import DbDao


class RoundDao(object):

    def __init__(self):
        self._dao = DbDao("Minesweeper", "Log")

    def SaveLog(self, player, roundId, action, **kwargs):
        log = {
            "Name": player.GetName(),
            "roundId": roundId,
            "Action": action,
            "CreateTime": datetime.datetime.now()
        }
        if kwargs is not None:
            log.update(kwargs)

        self._dao.Insert(log)
