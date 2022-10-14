import copy
import random


class GridManager(object):
    FLAG_CORRECT = 50
    FLAG_ERROR = -75
    CLICK_MINE = -250

    def __init__(self, width, height, mine_count):
        self._mine_count = mine_count
        self._mines_grid = []
        self._initGrids(width, height)

    def _initGrids(self, width, height):
        self._width = width
        self._height = height
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
                    "IsOpen": False,
                }

        # Generate mine
        mine_count = 0
        while mine_count < self._mine_count:
            grid = self._grids[random.randint(0, self._width - 1), random.randint(0, self._height - 1)]
            if grid["IsMine"]:
                continue
            grid["IsMine"] = True
            self._mines_grid.append(grid)
            adjacent_grids = self.GetAdjacentGrids(grid)
            for g in adjacent_grids:
                g["MineCount"] += 1
            mine_count += 1

    def _calcScore(self, grid, is_clicked):
        if grid is None:
            return 0

        score = 0
        if is_clicked:
            score += GridManager.CLICK_MINE if grid["IsMine"] else grid["MineCount"]
        else:
            score += GridManager.FLAG_CORRECT if grid["IsMine"] else GridManager.FLAG_ERROR

        return score

    def GetAdjacentGrids(self, grid):
        relatedPosition = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        eightGrids = []
        for i in range(len(relatedPosition)):
            item = self._grids.get((grid["X"] + relatedPosition[i][0], grid["Y"] + relatedPosition[i][1]), None)
            if item is not None:
                eightGrids.append(item)

        return eightGrids

    def GetGrids(self):
        return self._grids

    def RevealGrid(self, position):
        grid = self._grids.get(position, None)

        grid["IsOpen"] = True

        if grid["IsFlag"]:
            grid["IsFlag"] = False

        if not grid["IsMine"] and not grid["MineCount"] == 0:
            return self._calcScore(grid, True)

        if grid["IsMine"]:
            grid["IsMineClicked"] = True
            return self._calcScore(grid, True)

        score = 0
        for g in self.GetAdjacentGrids(grid):
            if not g["IsOpen"]:
                score += self.RevealGrid((g["X"], g["Y"]))
        return score

    def MarkGrid(self, position):
        grid = self._grids[position]
        grid["IsFlag"] = True
        grid["IsOpen"] = True
        return self._calcScore(grid, False)

    def IsAllGridsClicked(self):
        for grid in self._grids.values():
            if not grid["IsOpen"]:
                return False
        return True

    def _isValidGrid(self, position):
        grid = self._grids.get(position, None)
        if grid is None:
            return False

        return not grid["IsOpen"]

