from ManagerBase import ManagerBase
from Round import Game


class RoundManager(ManagerBase):
    def __init__(self, accountManager):
        super(RoundManager, self).__init__()
        self._nextRoundId = 1
        self._accountManager = accountManager
        self._allRounds = {}
        self._allPlayers = {}
        self.RegisterProcessMethod('Create', 'Post', self._create)
        self.RegisterProcessMethod('GetAllRound', 'Get', self._getAllRound)
        self.RegisterProcessMethod('Join', 'Post', self._join)
        self.RegisterProcessMethod('Leave', 'Post', self._leave)
        self.RegisterProcessMethod('GetJoinedRound', 'Get', self._getJoinedRound)
        self.RegisterProcessMethod('Open', 'Post', self._processAction)
        self.RegisterProcessMethod('SetFlag', 'Post', self._processAction)
        self.RegisterProcessMethod('Surrender', 'Post', self._surrender)

    def Process(self, **kwargs):
        funcName = kwargs['FuncName']
        if 'Token' in kwargs:
            player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
            kwargs['Player'] = player

        return self.AllProcessMethod[funcName]['_func'](**kwargs)

    def _join(self, **kwargs):
        player, roundId = kwargs['Player'], kwargs['RoundId']
        name = player.GetName()
        if roundId not in self._allRounds:
            return -101, None

        if name in self._allPlayers and \
                self._allPlayers[name] != self._allRounds[roundId] and \
                self._allPlayers[name].GetState() != "End":
            return -100, None

        game = self._allRounds[roundId]
        code = game.Join(player)
        if code >= 0:
            self._allPlayers[name] = game
        return code, None

    def _leave(self, **kwargs):
        player = kwargs['Player']
        name = player.GetName()
        if name not in self._allPlayers:
            return -104, None

        game = self._allPlayers[name]
        code = game.Leave(player)
        if code >= 0:
            del self._allPlayers[name]
        return code, None

    def _getAllRound(self, **kwargs):
        result = []
        for roundId, game in [(k, v) for k, v in self._allRounds.items() if v.GetState() != "End"]:
            info = game.GetInfo()
            info["RoundId"] = roundId
            result.append(info)

        return 0, {'Data': result}

    def _create(self, **kwargs):
        player = kwargs['Player']
        width, height, = kwargs['Width'], kwargs['Height']
        mineCount, playerCount, computerCount = kwargs['MineCount'], kwargs['PlayerCount'], kwargs['ComputerCount']

        name = player.GetName()
        if name in self._allPlayers and self._allPlayers[name].GetState() != "End":
            return -100, None

        if width < 5 or width > 20 or \
                height < 5 or height > 20 or \
                mineCount < 1 or mineCount > 20 or \
                playerCount < 1 or \
                computerCount < 0:
            return -105, None

        game = Game(width, height, mineCount, playerCount, computerCount)
        game.Join(player)
        roundId = self._nextRoundId
        self._nextRoundId += 1
        self._allRounds[roundId] = game
        self._allPlayers[player.GetName()] = game
        return 0, {'RoundId': roundId}

    def _processAction(self, **kwargs):
        player = kwargs['Player']
        x, y = kwargs['X'], kwargs['Y']
        action = kwargs['FuncName']
        if player.GetName() not in self._allPlayers:
            return -104, None

        game = self._allPlayers[player.GetName()]
        return game.ProcessPlayerAction(player, action, (x, y)), None

    def _getJoinedRound(self, **kwargs):
        player = kwargs['Player']
        if player.GetName() not in self._allPlayers:
            return None

        game = self._allPlayers[player.GetName()]
        return 0, {'Data': game.GetInfo()}

    def _surrender(self, **kwargs):
        player = kwargs['Player']
        if player.GetName() not in self._allPlayers:
            return -104, None

        game = self._allPlayers[player.GetName()]
        return game.Surrender(player), None
