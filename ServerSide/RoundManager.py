import json

import redis

from Computer import Computer
from Round import Round
from RoundDao import RoundDao


class RoundManager(object):
    ALL_ROUND_KEY = "AllRound"
    NEXT_ROUND_ID = "NextRoundId"

    def __init__(self, accountManager, registerFunc):
        super(RoundManager, self).__init__()
        self._nextRoundId = 1
        self._accountManager = accountManager
        self._allRounds = {}
        self._dao = RoundDao()
        self._redis = redis.Redis("localhost", 6379, decode_responses=True)
        namespace = "Round"
        registerFunc('Create', self.OnCreate, namespace=namespace)
        registerFunc('GetAllRound', self.OnGetAllRound, namespace=namespace)
        registerFunc('Join', self.OnJoin, namespace=namespace)
        registerFunc('Leave', self.OnLeave, namespace=namespace)
        registerFunc('GetRoundData', self.OnGetRoundData, namespace=namespace)
        registerFunc('OpenGrid', self.OnProcessAction, namespace=namespace)
        registerFunc('SetFlagGrid', self.OnProcessAction, namespace=namespace)
        registerFunc('Surrender', self.OnSurrender, namespace=namespace)
        self._restoreAllRound()

    def OnJoin(self, **kwargs):
        roundId = kwargs['RoundId']
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        if roundId not in self._allRounds:
            return -101, {"RoundId": None}

        joinedGame = self._getRound(player)
        if joinedGame is not None and \
                joinedGame.GetState() != "End" and \
                joinedGame != self._allRounds[roundId]:
            return -100, {"RoundId": None}

        game = self._allRounds[roundId]
        code = game.Join(player)

        self._saveRedis(game)
        return code, {"RoundId": roundId if code >= 0 else None}

    def OnLeave(self, **kwargs):
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])

        game = self._getRound(player)
        if game is None:
            return -104, None

        code = game.Leave(player)

        self._saveRedis(game)
        return code, None

    def OnGetAllRound(self, **kwargs):
        result = []
        for roundId, game in [(k, v) for k, v in self._allRounds.items() if v.GetState() != "End"]:
            info = game.GetInfo()
            result.append({
                "RoundId": roundId,
                "Players": [p.Serialize() for p in game.GetPlayers()],
                "State": game.GetState(),
                "PlayerCount": info["PlayerCount"],
                "ComputerCount": info["ComputerCount"],
            })

        return 0, {'Data': result}

    def OnCreate(self, **kwargs):
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        width, height, = kwargs['Width'], kwargs['Height']
        mineCount, playerCount, computerCount = kwargs['MineCount'], kwargs['PlayerCount'], kwargs['ComputerCount']

        game = self._getRound(player)
        if game is not None and game.GetState() != "End":
            return -100, None

        if width < 5 or width > 20 or \
                height < 5 or height > 20 or \
                mineCount < 1 or mineCount > 20 or \
                playerCount < 1 or \
                computerCount < 0:
            return -105, None

        roundId = self._nextRoundId
        self._nextRoundId += 1

        game = Round(width, height, mineCount, playerCount, computerCount)
        game.Join(player)

        self._allRounds[roundId] = game
        self._saveRedis(game, roundId)
        self._redis.set(RoundManager.NEXT_ROUND_ID, self._nextRoundId)
        return 0, {'RoundId': roundId}

    def OnProcessAction(self, **kwargs):
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        position = kwargs['X'], kwargs['Y']
        action = kwargs['Path'].split("/").pop()
        game = self._getRound(player)
        if game is None:
            return -104, None
        code = game.ProcessPlayerAction(player, action, position)

        self._saveRedis(game)
        return code, None

    def OnGetRoundData(self, **kwargs):
        roundId = kwargs.get('RoundId')
        if roundId is None or roundId not in self._allRounds:
            return -105, None

        game = self._allRounds[roundId]
        return 0, {'Data': game.GetInfo()}

    def OnSurrender(self, **kwargs):
        player = self._accountManager.GetPlayerInfoByToken(kwargs['Token'])
        if self._getRound(player) is None:
            return -104, None

        game = self._getRound(player)
        code = game.Surrender(player)

        self._saveRedis(game)
        return code, None

    def _getRound(self, player):
        return next((r for r in self._allRounds.values()
                     if player.GetName() in [p.GetName() for p in r.GetPlayers()] and
                     r.GetState() != "End"), None)

    def _restoreAllRound(self):
        allRound = self._redis.hgetall(RoundManager.ALL_ROUND_KEY)
        nextId = self._redis.get(RoundManager.NEXT_ROUND_ID)
        self._nextRoundId = int(nextId) if nextId is not None else 0

        for key, value in allRound.items():
            players = []
            info = json.loads(value)
            for p in info["Players"]:
                if p["IsComputer"]:
                    players.append(Computer(p["Name"]))
                else:
                    players.append(self._accountManager.GetPlayerInfoByName(p["Name"]))
            self._allRounds[int(key)] = Round.Restore(info, players)

    def _saveRedis(self, game, roundId=None):
        if roundId is None:
            roundId = next((key for key, value in self._allRounds.items() if value == game))

        self._redis.hset(RoundManager.ALL_ROUND_KEY, roundId, json.dumps(game.GetInfo()))

