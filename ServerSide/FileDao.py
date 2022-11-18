import json
import os

from IDao import IDao


class FileDao(IDao):
    PLAYER_ROOT = "Players"

    def Insert(self, key, data, force=False):
        path = os.path.join(FileDao.PLAYER_ROOT, key + ".json")

        if not force and os.path.exists(path):
            print "{} is exists".format(key)
            return False

        fp = open(path, "w+")
        fp.write(json.dumps(data))
        return True

    def FindAll(self, filterFunc=None):
        result = []
        for path in os.listdir(FileDao.PLAYER_ROOT):
            data = json.load(open(path, "r"))
            if filterFunc is None or filterFunc(data):
                result.append(data)

        return result

    def FindByKey(self, key):
        path = os.path.join(FileDao.PLAYER_ROOT, key + ".json")
        return json.load(open(path, "r")) if os.path.exists(path) else None

    def DeleteByKey(self, key):
        path = os.path.join(FileDao.PLAYER_ROOT, key + ".json")
        if not os.path.exists(path):
            return False

        os.remove(path)
        return True
