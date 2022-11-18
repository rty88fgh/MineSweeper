from Round import Round


class RoundManager(object):
    def __init__(self, accountManager, registerFunc):
        super(RoundManager, self).__init__()
        self._nextRoundId = 1
        self._accountManager = accountManager
        self._allRounds = {}
        registerFunc('Create', self._create)
        registerFunc('GetAllRound', self._getAllRound)
        registerFunc('Join', self._join)
        registerFunc('Leave', self._leave)
        registerFunc('GetRoundData', self._getRoundData)
        registerFunc('OpenGrid', self._processAction)
        registerFunc('SetFlagGrid', self._processAction)
        registerFunc('Surrender', self._surrender)

    def _join(self, **kwargs):
        roundId = kwargs['RoundId']
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        name = player.GetName()
        if roundId not in self._allRounds:
            return -101, {"RoundId": None}

        allPlayers = self._getAllPlayers()

        if name in allPlayers and \
                allPlayers[name] != self._allRounds[roundId] and \
                allPlayers[name].GetState() != "End":
            return -100, {"RoundId": None}

        game = self._allRounds[roundId]
        code = game.Join(player)
        return code, {"RoundId": roundId if code >= 0 else None}

    def _leave(self, **kwargs):
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        name = player.GetName()
        if name not in self._allPlayers:
            return -104, None

        game = self._getAllPlayers()[name]
        code = game.Leave(player)
        return code, None

    def _getAllRound(self, **kwargs):
        result = []
        for roundId, game in [(k, v) for k, v in self._allRounds.items() if v.GetState() != "End"]:
            result.append({
                "RoundId": roundId,
                "Players": [p.Serialize() for p in game.GetPlayers()],
                "Status": game.GetState(),
            })

        return 0, {'Data': result}

    def _create(self, **kwargs):
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        width, height, = kwargs['Width'], kwargs['Height']
        mineCount, playerCount, computerCount = kwargs['MineCount'], kwargs['PlayerCount'], kwargs['ComputerCount']

        name = player.GetName()
        if name in self._getAllPlayers().keys() and self._getAllPlayers()[name].GetState() != "End":
            return -100, None

        if width < 5 or width > 20 or \
                height < 5 or height > 20 or \
                mineCount < 1 or mineCount > 20 or \
                playerCount < 1 or \
                computerCount < 0:
            return -105, None

        game = Round(width, height, mineCount, playerCount, computerCount)
        game.Join(player)
        roundId = self._nextRoundId
        self._nextRoundId += 1
        self._allRounds[roundId] = game
        self._getAllPlayers()[player.GetName()] = game
        return 0, {'RoundId': roundId}

    def _processAction(self, **kwargs):
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        x, y = kwargs['X'], kwargs['Y']
        action = kwargs['Path'].replace("/", "")
        if player.GetName() not in self._getAllPlayers():
            return -104, None

        game = self._getAllPlayers()[player.GetName()]
        return game.ProcessPlayerAction(player, action, (x, y)), None

    def _getRoundData(self, **kwargs):
        roundId = kwargs.get('RoundId', None)
        if roundId is None or roundId not in self._allRounds:
            return -105, None

        game = self._allRounds[roundId]
        return 0, {'Data': game.GetInfo()}

    def _surrender(self, **kwargs):
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        if player.GetName() not in self._getAllPlayers():
            return -104, None

        game = self._getAllPlayers()[player.GetName()]
        return game.Surrender(player), None

    def _getAllPlayers(self):
        allPlayers = {}
        for roundInfo in self._allRounds.values():
            players = roundInfo.GetPlayers()
            for p in players:
                allPlayers[p.GetName()] = roundInfo

        return allPlayers
