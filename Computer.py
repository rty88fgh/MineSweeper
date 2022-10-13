import gevent

from GridManager import GridManager
from Player import Player


class Computer(Player):
    def __init__(self, name):
        super(Computer, self).__init__(name, True)

    def GetComputerActionPosition(self, grids):
        set_flag = []
        must_not_mine = []
        unknown_girds = []

        gevent.sleep(1)
        ClickGrid = "ClickGrid"
        Flag = "Flag"

        for grid in grids.values():
            adjacent_grids = grid["AdjacentGrids"]
            if grid["IsClicked"]:
                if len([g for g in adjacent_grids if g["IsClicked"]]) == len(adjacent_grids):
                    continue

                is_click_or_flag_mine = [g for g in adjacent_grids if g["IsMine"] and (g["IsFlag"] or g["IsClicked"])]
                if len(is_click_or_flag_mine) - grid["MineCount"] == 0 and grid["MineCount"] > 0:
                    extend_list = [g for g in adjacent_grids if not g["IsClicked"]]
                    must_not_mine.extend(extend_list)

                nonClicked_grids = [g for g in adjacent_grids if not g["IsClicked"]]
                if grid["MineCount"] - len(is_click_or_flag_mine) == len(nonClicked_grids):
                    set_flag.extend(nonClicked_grids)

            else:
                # find flag
                if len([g for g in adjacent_grids if g["IsClicked"] and not g["IsMine"]]) == len(adjacent_grids):
                    set_flag.append(grid)

                if len([g for g in adjacent_grids if not g["IsClicked"]]) == len(adjacent_grids):
                    unknown_girds.append(grid)

        if len(set_flag) > 0:
            select_grid = set_flag[0]
            return Flag, (select_grid["X"], select_grid["Y"])

        elif len(must_not_mine) > 0:
            select_grid = must_not_mine[0]
            return ClickGrid, (select_grid["X"], select_grid["Y"])

        elif len(unknown_girds) > 0:
            select_grid = unknown_girds[0]
            return ClickGrid, (select_grid["X"], select_grid["Y"])
        else:
            # calculate probability
            have_mine_count_grid = [g for g in grids if g["IsClicked"] and g["MineCount"] > 0]
            probability_dict = {}
            for grid in have_mine_count_grid:
                adjacent_grids = grid["AdjacentGrids"]
                not_clicked = [g for g in adjacent_grids if not g["IsClicked"]]
                # all grids were clicked
                if len(not_clicked) == 0:
                    continue

                clicked_grid_count = len(adjacent_grids) - len(not_clicked)

                is_mine_clicked = [g for g in adjacent_grids if g["IsMine"] and g["IsClicked"]]
                probability = float(grid["MineCount"] - len(is_mine_clicked)) / float(
                    len(adjacent_grids) - clicked_grid_count)
                for ag in not_clicked:
                    xy = ag["X"], ag["Y"]
                    # it will override the probability if adjacent grid has high probability
                    if xy not in probability_dict or probability > probability_dict[xy]:
                        probability_dict[xy] = probability

            # find less probability of grid
            nonclicked_grid = [pair for pair in probability_dict.items()]
            nonclicked_grid.sort(key=lambda p: p[1])
            print nonclicked_grid[0]
            return (Flag if nonclicked_grid[0][1] == float(1) else ClickGrid), nonclicked_grid[0][0]
