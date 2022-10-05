import random

from Grid import Grid


class GameScore(object):
    FlagCorrect = "FlagCorrect"
    FlagError = "FlagError"
    ClickMine = "MineError"
    ScoreMap = {
        FlagCorrect: 50,
        FlagError: -75,
        ClickMine: -250
    }


class GridContainer(object):
    def __init__(self, width, height, mine_count):
        self._grids = []
        self._width = width
        self._height = height
        self._mine_count = mine_count
        self._mines_grid = []

    def get_grids(self):
        return self._grids

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
                if x > self._width - 1 or y > self._height - 1 or x < 0 or y < 0:
                    continue
                grids.append(self._grids[x][y])

        return grids

    def reveal_grid(self, grid):
        if grid.get_is_clicked():
            return 0

        grid.set_is_clicked(True)
        if grid.get_is_flag():
            grid.set_is_flag(False)

        if grid.get_is_mine():
            grid.set_is_mine_clicked(True)
            return GameScore.ScoreMap[GameScore.ClickMine]
        elif grid.get_mine_count() == 0:
            nearby_grids = self.get_nearby_grids(grid)
            score = 0
            for g in nearby_grids:
                if not g.get_is_clicked():
                    score += self.reveal_grid(g)
            return score

        else:
            return grid.get_mine_count()

    def set_flag(self, grid):
        if grid.get_is_clicked():
            return 0
        grid.set_is_flag(True)
        grid.set_is_clicked(True)
        return GameScore.ScoreMap[GameScore.FlagCorrect] if grid.get_is_mine() else GameScore.ScoreMap[GameScore.FlagError]

    def check_all_flag_clicked(self):
        for x in range(self._width):
            for y in range(self._height):
                if not self._grids[x][y].get_is_clicked():
                    return False
        return True
