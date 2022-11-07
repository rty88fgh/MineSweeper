from Player import Player


class Computer(Player):
    def __init__(self, name, gridManager):
        super(Computer, self).__init__(name, True)
        self._gridManager = None
        self._gridManager = gridManager

    def ProcessAction(self):
        set_flag = []
        must_not_mine = []
        unknown_girds = []
        grids = self._gridManager.GetGrids()

        for grid in grids.values():
            adjacent_grids = self._gridManager.GetAdjacentGrids(grid)
            isOpen = grid["IsOpen"]
            mineCount = grid["MineCount"]
            if isOpen:
                if len([g for g in adjacent_grids if g["IsOpen"]]) == len(adjacent_grids):
                    continue

                is_click_or_flag_mine = [g for g in adjacent_grids if g["IsMine"] and (g["IsFlag"] or g["IsOpen"])]
                if len(is_click_or_flag_mine) - mineCount == 0 and mineCount > 0:
                    extend_list = [g for g in adjacent_grids if not g["IsOpen"]]
                    must_not_mine.extend(extend_list)

                nonClicked_grids = [g for g in adjacent_grids if not g["IsOpen"]]
                if mineCount - len(is_click_or_flag_mine) == len(nonClicked_grids):
                    set_flag.extend(nonClicked_grids)

            else:
                # find flag
                if len([g for g in adjacent_grids if g["IsOpen"] and not g["IsMine"]]) == len(adjacent_grids):
                    set_flag.append(grid)

                if len([g for g in adjacent_grids if not g["IsOpen"]]) == len(adjacent_grids):
                    unknown_girds.append(grid)

        if len(set_flag) > 0:
            select_grid = set_flag[0]
            return "Flag", (select_grid["X"], select_grid["Y"])

        elif len(must_not_mine) > 0:
            select_grid = must_not_mine[0]
            return "Click", (select_grid["X"], select_grid["Y"])

        elif len(unknown_girds) > 0:
            select_grid = unknown_girds[0]
            return "Click", (select_grid["X"], select_grid["Y"])
        else:
            # calculate probability
            have_mine_count_grid = [g for g in grids if g["IsOpen"] and g["MineCount"] > 0]
            probability_dict = {}
            for grid in have_mine_count_grid:
                adjacent_grids = self._gridManager.GetAdjacentGrids(grid)
                not_clicked = [g for g in adjacent_grids if not g["IsOpen"]]
                # all grids were clicked
                if len(not_clicked) == 0:
                    continue

                clicked_grid_count = len(adjacent_grids) - len(not_clicked)

                is_mine_clicked = [g for g in adjacent_grids if g["IsMine"] and g["IsOpen"]]
                probability = float(mineCount - len(is_mine_clicked)) / float(
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
            return ("Flag" if nonclicked_grid[0][1] == float(1) else "Click"), nonclicked_grid[0][0]
