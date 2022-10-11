class Player(object):
    def __init__(self, name, is_computer=False):
        self._name = name
        self._score = 0
        self._is_computer = is_computer

    def GetName(self):
        return self._name

    def GetScore(self):
        return self._score

    def IsComputer(self):
        return self._is_computer

    def SubScore(self, value):
        if value < 0:
            return False
        self._calcScore(value * -1)
        return True

    def AddScore(self, value):
        if value < 0:
            return False

        self._calcScore(value)
        return True

    def ResetScore(self):
        self._score = 0

    def _calcScore(self, value):
        self._score += value
