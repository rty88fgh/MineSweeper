class Player(object):
    def __init__(self, name, isComputer=False):
        self._name = name
        self._score = 0
        self._isComputer = isComputer

    def GetName(self):
        return self._name

    def GetScore(self):
        return self._score

    def IsComputer(self):
        return self._isComputer

    def SubScore(self, value):
        if value < 0:
            return False, self._score

        self._calcScore(-value)
        return True, self._score

    def AddScore(self, value):
        if value < 0:
            return False, self._score

        self._calcScore(value)
        return True, self._score

    def ResetScore(self):
        self._score = 0

    def Serialize(self):
        return {
            "name": self._name,
            "score": self._score,
            "isComputer": self._isComputer
        }

    def _calcScore(self, value):
        self._score += value
