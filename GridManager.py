import copy
import random


class GridManager(object):
    def __init__(self, width, height, mine_count):
        self._grids = {}
        self._width = width
        self._height = height
        self._mine_count = mine_count
        self._mines_grid = []

    def GetGrids(self):
        return self._grids

    def GetWidth(self):
        return self._width

    def GetHeight(self):
        return self._height

    def InitGrids(self):
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
            adjacent_grids = self.GetAdjacentGrids(grid)
            for g in adjacent_grids:
                g["MineCount"] += 1
            mine_count += 1

    def RevealGrid(self, position):
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
            for g in self.GetAdjacentGrids(grid):
                if not g["IsClicked"]:
                    touch_grids.extend(self.RevealGrid((g["X"], g["Y"])))
        else:
            touch_grids.append(grid)

        return touch_grids

    def Mark(self, position):
        grid = self._grids[position]
        if grid["IsClicked"]:
            return []
        grid["IsFlag"] = True
        grid["IsClicked"] = True
        return [grid]

    def IsAllGridsClicked(self):
        for x in range(self._width):
            for y in range(self._height):
                if not self._grids[(x, y)]["IsClicked"]:
                    return False
        return True

    def GetAdjacentGrids(self, grid):
        grids = []
        for x in [grid["X"] - 1, grid["X"], grid["X"] + 1]:
            for y in [grid["Y"] - 1, grid["Y"], grid["Y"] + 1]:
                if x == grid["X"] and y == grid["Y"]:
                    continue
                if x > self._width - 1 or y > self._height - 1 or x < 0 or y < 0:
                    continue
                grids.append(self._grids[(x, y)])

        return grids

