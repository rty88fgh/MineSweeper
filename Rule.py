class Rule(object):
    FlagCorrect = "FlagCorrect"
    FlagError = "FlagError"
    ClickMine = "MineError"
    ScoreMap = {
        FlagCorrect: 50,
        FlagError: -75,
        ClickMine: -250
    }

    @staticmethod
    def CalculateScore(grids, is_clicked):
        if grids is None:
            return 0

        score = 0
        for grid in grids:
            if is_clicked:
                if grid["IsMine"] and is_clicked:
                    score += Rule.ScoreMap[Rule.ClickMine]
                else:
                    score += grid["MineCount"]
            else:
                if grid["IsMine"] and not is_clicked:
                    score += Rule.ScoreMap[Rule.FlagCorrect]
                else:
                    score += Rule.ScoreMap[Rule.FlagError]

        return score
