class Player(object):
    def __init__(self, name):
        self._name = name
        self._score = 0

    def get_name(self):
        return self._name

    def get_score(self):
        return self._score

    def add_score(self, value):
        self._score += value

    def reset_score(self):
        self._score = 0
