import copy
import random

random.seed(10)
class GridContainer(object):
    def __init__(self, width, height, mine_count):
        self._grids = {}
        self._width = width
        self._height = height
        self._mine_count = mine_count
        self._mines_grid = []

    def get_grids(self):
        return self._grids

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def init_grids(self):
        self._grids = {}
        for x in range(self._width):
            for y in range(self._height):
                self._grids[(x, y)] = {
                    "X": x,
                    "Y": y,
                    "IsMine": False,
                    "IsFlag": False,
                    "IsMineClicked": False,
                    "MineCount": 0,
                    "IsClicked": False,
                }

        # Generate mine
        mine_count = 0
        while mine_count < self._mine_count:
            grid = self._grids[random.randint(0, self._width - 1), random.randint(0, self._width - 1)]
            if grid["IsMine"]:
                continue
            grid["IsMine"] = True
            self._mines_grid.append(grid)
            adjacent_grids = self.get_adjacent_grids(grid)
            for g in adjacent_grids:
                g["MineCount"] += 1
            mine_count += 1

    def get_adjacent_grids(self, grid):
        grids = []
        for x in [grid["X"] - 1, grid["X"], grid["X"] + 1]:
            for y in [grid["Y"] - 1, grid["Y"], grid["Y"] + 1]:
                if x == grid["X"] and y == grid["Y"]:
                    continue
                if x > self._width - 1 or y > self._height - 1 or x < 0 or y < 0:
                    continue
                grids.append(self._grids[(x, y)])

        return grids

    def reveal_grid_and_get_touch_grids(self, position):
        grid = self._grids.get(position, None)
        if grid is None:
            return []

        if grid["IsClicked"]:
            return []
        touch_grids = []
        grid["IsClicked"] = True
        if grid["IsFlag"]:
            grid["IsFlag"](False)

        if grid["IsMine"]:
            grid["IsMineClicked"] = True
            touch_grids.append(grid)
        elif grid["MineCount"] == 0:
            for g in self.get_adjacent_grids(grid):
                if not g["IsClicked"]:
                    touch_grids.extend(self.reveal_grid_and_get_touch_grids((g["X"], g["Y"])))
        else:
            touch_grids.append(grid)

        return touch_grids

    def set_flag_get_touch_grid(self, position):
        grid = self._grids[position]
        if grid["IsClicked"]:
            return []
        grid["IsFlag"] = True
        grid["IsClicked"] = True
        return [grid]

    def is_all_grid_clicked(self):
        for x in range(self._width):
            for y in range(self._height):
                if not self._grids[(x, y)]["IsClicked"]:
                    return False
        return True
