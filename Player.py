class Player(object):
    def __init__(self, name, is_computer=False):
        self._name = name
        self._score = 0
        self._is_computer = is_computer

    def get_name(self):
        return self._name

    def get_score(self):
        return self._score

    def get_is_computer(self):
        return self._is_computer

    def add_score(self, value):
        self._score += value

    def reset_score(self):
        self._score = 0
