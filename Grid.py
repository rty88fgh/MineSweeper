class Grid(object):
    def __init__(self, nX, nY):
        self._nX = nX
        self._nY = nY
        self._is_mine = False
        self._is_clicked = False
        self._is_flag = False
        self._is_mine_clicked = False
        self._mine_count = 0

    def get_x(self):
        return self._nX

    def get_y(self):
        return self._nY

    def get_is_mine(self):
        return self._is_mine

    def get_is_clicked(self):
        return self._is_clicked

    def get_is_flag(self):
        return self._is_flag

    def get_is_mine_clicked(self):
        return self._is_mine_clicked

    def get_mine_count(self):
        return self._mine_count

    def add_mine_count(self):
        self._mine_count += 1

    def set_is_mine(self, value):
        self._is_mine = value

    def set_is_flag(self, value):
        self._is_flag = value

    def set_is_mine_clicked(self, value):
        self._is_mine_clicked = value

    def set_is_clicked(self, value):
        self._is_clicked = value