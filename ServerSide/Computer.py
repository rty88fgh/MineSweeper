
from Player import Player

class Computer(Player):
    def __init__(self, name):
        super(Computer, self).__init__(name, True)

    def GetActPos(self, grids, getAdjacentGridsFunc):
        set_flag = []
        must_not_mine = []
        unknown_girds = []

        for grid in grids.values():
            adjacent_grids = getAdjacentGridsFunc(grid)
            if grid["isOpen"]:
                if len([g for g in adjacent_grids if g["isOpen"]]) == len(adjacent_grids):
                    continue

                is_click_or_flag_mine = [g for g in adjacent_grids if g["isMine"] and (g["isFlag"] or g["isOpen"])]
                if len(is_click_or_flag_mine) - grid["mineCount"] == 0 and grid["mineCount"] > 0:
                    extend_list = [g for g in adjacent_grids if not g["isOpen"]]
                    must_not_mine.extend(extend_list)

                nonClicked_grids = [g for g in adjacent_grids if not g["isOpen"]]
                if grid["mineCount"] - len(is_click_or_flag_mine) == len(nonClicked_grids):
                    set_flag.extend(nonClicked_grids)

            else:
                # find flag
                if len([g for g in adjacent_grids if g["isOpen"] and not g["isMine"]]) == len(adjacent_grids):
                    set_flag.append(grid)

                if len([g for g in adjacent_grids if not g["isOpen"]]) == len(adjacent_grids):
                    unknown_girds.append(grid)

        if len(set_flag) > 0:
            select_grid = set_flag[0]
            return "Flag", (select_grid["x"], select_grid["y"])

        elif len(must_not_mine) > 0:
            select_grid = must_not_mine[0]
            return "Click", (select_grid["x"], select_grid["y"])

        elif len(unknown_girds) > 0:
            select_grid = unknown_girds[0]
            return "Click", (select_grid["x"], select_grid["y"])
        else:
            # calculate probability
            have_mine_count_grid = [g for g in grids if g["isOpen"] and g["mineCount"] > 0]
            probability_dict = {}
            for grid in have_mine_count_grid:
                adjacent_grids = getAdjacentGridsFunc(grid)
                not_clicked = [g for g in adjacent_grids if not g["isOpen"]]
                # all grids were clicked
                if len(not_clicked) == 0:
                    continue

                clicked_grid_count = len(adjacent_grids) - len(not_clicked)

                is_mine_clicked = [g for g in adjacent_grids if g["isMine"] and g["isOpen"]]
                probability = float(grid["mineCount"] - len(is_mine_clicked)) / float(
                    len(adjacent_grids) - clicked_grid_count)
                for ag in not_clicked:
                    xy = ag["x"], ag["y"]
                    # it will override the probability if adjacent grid has high probability
                    if xy not in probability_dict or probability > probability_dict[xy]:
                        probability_dict[xy] = probability

            # find less probability of grid
            nonclicked_grid = [pair for pair in probability_dict.items()]
            nonclicked_grid.sort(key=lambda p: p[1])
            print nonclicked_grid[0]
            return ("Flag" if nonclicked_grid[0][1] == float(1) else "Click"), nonclicked_grid[0][0]
