import json
import os

from IDao import IDao


class FileDao(IDao):
    def __init__(self, root, extension):
        self._root = root
        self._extension = extension

    def Insert(self, data, **kwargs):
        fileName = kwargs.get("FileName", "")
        path = os.path.join(self._root, fileName + "." + self._extension)

        if os.path.exists(path):
            print "{} is exists".format(fileName)
            return False

        fp = open(path, "w+")
        fp.write(json.dumps(data))
        return True

    def FindAll(self, filterFunc=None, **kwargs):
        result = []
        for path in os.listdir(self._root):
            data = json.load(open(path, "r"))
            if filterFunc is None or filterFunc(data):
                result.append(data)

        return result

    def Find(self, key, **kwargs):
        path = os.path.join(self._root, key + "." + self._extension)
        return json.load(open(path, "r")) if os.path.exists(path) else None

    def Delete(self, key, **kwargs):
        path = os.path.join(self._root, key + "." + self._extension)
        if not os.path.exists(path):
            return False

        os.remove(path)
        return True

    def Update(self, key, data, **kwargs):
        path = os.path.join(self._root, key + "." + self._extension)
        path = os.path.join(self._root, key + "." + self._extension)
        if not os.path.exists(path):
            return False

        fp = open(path, "w+")
        fp.write(json.dumps(data))
        return True
