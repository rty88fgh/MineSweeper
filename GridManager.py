import copy
import random


class GridManager(object):
    FLAGCORRECT = 50
    flagError = -75
    clickMine = -250

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
                    "IsClicked": False,  # IsOpen
                    "AdjacentGrids": []
                }

        # Generate adjacent grids
        for grid in self._grids.values():
            grid["AdjacentGrids"] = self._getAdjacentGrids(grid)

        # Generate mine
        mine_count = 0
        while mine_count < self._mine_count:
            grid = self._grids[random.randint(0, self._width - 1), random.randint(0, self._height - 1)]
            if grid["IsMine"]:
                continue
            grid["IsMine"] = True
            self._mines_grid.append(grid)
            adjacent_grids = grid["AdjacentGrids"]
            for g in adjacent_grids:
                g["MineCount"] += 1
            mine_count += 1

    def _calcScore(self, grid, is_clicked):
        if grid is None:
            return 0

        score = 0
        if is_clicked:
            score += GridManager.clickMine if grid["IsMine"] else grid["MineCount"]
        else:
            score += GridManager.FLAGCORRECT if grid["IsMine"] else GridManager.flagError

        return score

    def _getAdjacentGrids(self, grid):
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
        if grid is None:
            return 0

        if grid["IsClicked"]:
            return 0

        grid["IsClicked"] = True

        if grid["IsFlag"]:
            grid["IsFlag"] = False

        if not grid["IsMine"] and not grid["MineCount"] == 0:
            return self._calcScore(grid, True)

        if grid["IsMine"]:
            grid["IsMineClicked"] = True
            return self._calcScore(grid, True)

        score = 0
        for g in grid["AdjacentGrids"]:
            if not g["IsClicked"]:
                score += self.RevealGrid((g["X"], g["Y"]))
        return score

    def MarkGrid(self, position):
        grid = self._grids[position]
        if grid["IsClicked"]:
            return 0
        grid["IsFlag"] = True
        grid["IsClicked"] = True
        return self._calcScore(grid, False)

    def IsAllGridsClicked(self):
        for grid in self._grids.values():
            if not grid["IsClicked"]:
                return False
        return True
