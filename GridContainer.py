import random

from Grid import Grid


class GridContainer(object):
    def __init__(self, width, height, mine_count):
        self._grids = []
        self._width = width
        self._height = height
        self._mine_count = mine_count
        self._mines_grid = []
        self._flag_grid = []

    def get_grids(self):
        return self._grids

    def get_mine_left_count(self):
        return self._mine_count - len(self._flag_grid)

    def init_grids(self):
        self._grids = []
        for x in range(self._width):
            row_mine = []
            for y in range(self._height):
                row_mine.append(Grid(x, y))
            self._grids.append(row_mine)

        # Generate mine
        mine_count = 0
        while mine_count < self._mine_count:
            grid = self._grids[random.randint(0, self._width - 1)][random.randint(0, self._width - 1)]
            if grid.get_is_mine():
                continue
            grid.set_is_mine(True)
            self._mines_grid.append(grid)
            nearby_grids = self.get_nearby_grids(grid)
            for g in nearby_grids:
                g.add_mine_count()
            mine_count += 1

    def get_nearby_grids(self, grid):
        grids = []
        for x in [grid.get_x() - 1, grid.get_x(), grid.get_x() + 1]:
            for y in [grid.get_y() - 1, grid.get_y(), grid.get_y() + 1]:
                if x == grid.get_x() and y == grid.get_y():
                    continue
                if x > self._width - 1 or y > self._height - 1 or x < 0  or y < 0:
                    continue
                grids.append(self._grids[x][y])

        return grids

    def reveal_grid(self, grid):
        grid.set_is_clicked(True)
        if grid.get_is_flag():
            grid.set_is_flag(False)
            self._flag_grid.remove(grid)

        if grid.get_is_mine():
            for mine in self._mines_grid:
                if mine.get_x() == grid.get_x() and mine.get_y() == grid.get_y():
                    mine.set_is_mine_clicked(True)
                else:
                    mine.set_is_clicked(True)
        elif grid.get_mine_count() == 0:
            nearby_grids = self.get_nearby_grids(grid)
            for g in nearby_grids:
                if not g.get_is_clicked():
                    self.reveal_grid(g)

    def set_flag(self, grid):
        if len(self._flag_grid) == self._mine_count:
            return
        if grid.get_is_flag():
            return

        grid.set_is_flag(True)
        self._flag_grid.append(grid)

    def set_all_flag_clicked(self):
        for flag in self._flag_grid:
            flag.set_is_clicked(True)

    def check_is_game_over(self):
        is_clicked_grids = [x for x in self._mines_grid if x.get_is_clicked() and not x.get_is_flag()]
        return len(is_clicked_grids) > 0

    def check_is_win(self):
        flag_mines = [x for x in self._mines_grid if x.get_is_flag()]
        if len(flag_mines) == self._mine_count:
            return True

        for x in range(self._width):
            for y in range(self._height):
                if not self._grids[x][y].get_is_clicked():
                    return False
        return True
