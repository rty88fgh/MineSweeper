class Player(object):
    def __init__(self, name, is_computer=False):
        self._name = name
        self._score = 0
        self._is_computer = is_computer

    def GetName(self):
        return self._name

    def GetScore(self):
        return self._score

    def GetIsComputer(self):
        return self._is_computer

    def AddScore(self, value):
        self._score += value

    def ResetScore(self):
        self._score = 0
