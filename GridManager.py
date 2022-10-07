import copy
import random


class GridManager(object):
    def __init__(self, width, height, mine_count):
        self._mine_count = mine_count
        self._mines_grid = []
        self._initGrids(width, height)

    def GetGrids(self):
        return self._grids

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
            adjacent_grids = GridManager.GetAdjacentGrids(grid, self._grids)
            for g in adjacent_grids:
                g["MineCount"] += 1
            mine_count += 1

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
        for g in self.GetAdjacentGrids(grid, self._grids):
            if not g["IsClicked"]:
                score += self.RevealGrid((g["X"], g["Y"]))
        return score

    def MarkGrid(self, position):
        grid = self._grids[position]
        if grid["IsClicked"]:
            return []
        grid["IsFlag"] = True
        grid["IsClicked"] = True
        return self._calcScore(grid, False)

    def IsAllGridsClicked(self):
        for x in range(self._width):
            for y in range(self._height):
                if not self._grids[(x, y)]["IsClicked"]:
                    return False
        return True

    def _calcScore(self, grid, is_clicked):

        if grid is None:
            return 0

        flagCorrect = "FlagCorrect"
        flagError = "FlagError"
        clickMine = "MineError"
        scoreMap = {
            flagCorrect: 50,
            flagError: -75,
            clickMine: -250
        }

        score = 0
        if is_clicked:
            score += scoreMap[clickMine] if grid["IsMine"] else grid["MineCount"]
        else:
            score += scoreMap[flagCorrect] if grid["IsMine"] else scoreMap[flagError]

        return score

    @staticmethod
    def GetAdjacentGrids(grid, allGrids):
        eightGrids = [g for g in allGrids.values() if
                      abs(g["X"] - grid["X"]) <= 1 and
                      abs(g["Y"] - grid["Y"]) <= 1 and
                      not (g["X"] == grid["X"] and g["Y"] == grid["Y"])]

        return eightGrids
