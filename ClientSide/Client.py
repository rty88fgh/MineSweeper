import json
from hashlib import md5
import gevent
import requests
from View import View


class Client(object):
    ServerUrl = "http://127.0.0.1:6060"

    def __init__(self):
        self._view = View()
        self._playerName = ""
        self._lastUpdateTime = 0
        self._token = None
        self._joinedRoundId = None
        self._codeDict = {
            100: "Player joined back",
            -100: "Player has joined other game.",
            -101: "RoundId did not found.",
            -103: "Round is not playing",
            -102: "Joined round cannot leave",
            -104: "Player did not join round",
            -105: "Parameter error",
            -106: "It not your turn",
            -107: "Position error",
            -109: "Player name is duplicate.",
            -110: "Login Failed",
            -111: "Error while create account",
        }

    def Run(self):
        while True:
            print "===================="
            menuAns = self._view.ConsoleMenu(["Register", "Login"])
            if menuAns == 0 and self._register():
                break
            elif menuAns == 1 and self._login():
                break

        while True:
            resp = self._sendService("/Round/GetAllRound", requests.post)

            if resp is None or resp['Code'] < 0:
                print "Failed to get all rounds. It will retry 1 sec..."
                gevent.sleep(1)
                continue

            roundsInfo = resp["Data"]

            print "Rounds:"
            for info in roundsInfo:
                players = info["Players"]
                print "Round Id:{} State:{} Players:{} PlayerCount:{} ComputerCount:{}".format(
                    info["RoundId"],
                    info["State"],
                    "".join(
                        [p["Name"] + "," if p["Name"] != players[len(players) - 1] else p["Name"] for p in players]),
                    info["PlayerCount"],
                    info["ComputerCount"])

            menuAns = self._view.ConsoleMenu(["Create new game", "Join", "Left"])
            if menuAns == 0 and self._createGame():
                break
            elif menuAns == 1 and self._joinGame([int(i["RoundId"]) for i in roundsInfo]):
                break
            elif menuAns == 2:
                self._leftGame()

        print "Waiting for start..."

        isInit = False
        while True:
            resp = self._sendService("/Round/GetRoundData",
                                     requests.post,
                                     data={"RoundId": self._joinedRoundId},
                                     printLog=False)

            if resp is None:
                print "Failed to get joined round. It will retry 1 sec..."
                gevent.sleep(1)
                continue
            info = resp["Data"]
            if info["State"] == "Init":
                gevent.sleep(1)
                continue

            if not isInit:
                self._view.InitPyGame(info["Width"], info["Height"], self._playerName)
                isInit = True

            if info["LastUpdateTime"] != self._lastUpdateTime:
                self._view.RefreshView(info["Grids"],
                                       info["Players"],
                                       info["Current"],
                                       info["ScoreMsg"],
                                       info["Winner"])
                self._lastUpdateTime = info["LastUpdateTime"]
                gevent.sleep(1)
                continue
            else:
                action, pos = self._view.ProcessAction()
                if action is None:
                    continue

            if action == View.Quit:
                self._view.CloseWindows()
                return
            elif action == View.Surrender:
                self._sendService("/Round/Surrender", requests.post, )
                continue

            self._sendService("/Round/" + action, requests.post, data={
                "X": pos[0],
                "Y": pos[1],
            }, printLog=False)

    def _register(self):
        name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
        password = self._view.GetPlayerAnswer("Password: ", isStr=True, defaultValue="1234")
        algo = md5()
        algo.update(password)

        resp = self._sendService("/Account/Register", requests.post, data={
            "Name": name,
            "Password": algo.hexdigest()
        }, useAuth=False)

        if resp is None:
            return False

        return self._login(name=name, password=password) if resp["Code"] >= 0 else False

    def _login(self, name=None, password=None):
        if name is None:
            name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
        if password is None:
            password = self._view.GetPlayerAnswer("Password: ", isStr=True, defaultValue="1234")

        algo = md5()
        algo.update(password)

        resp = self._sendService("/Account/Login", requests.post, data={
            "Name": name,
            "Password": algo.hexdigest()
        }, useAuth=False)

        if resp is not None and resp["Code"] >= 0:
            self._playerName = name
            self._token = resp["Token"]

        return False if resp is None else resp["Code"] >= 0

    def _createGame(self):
        widthCount = self._view.GetPlayerAnswer("Please enter width count (5 ~ 20, default: 10):", 10)
        heightCount = self._view.GetPlayerAnswer("Please enter height count (5 ~ 20, default: 10):", 10)
        mineCount = self._view.GetPlayerAnswer("Please enter mine count (1 ~ 20, default: 9):", 9)
        playerCount = self._view.GetPlayerAnswer("Please enter player count (default: 2):", 2)
        computerCount = self._view.GetPlayerAnswer("Please enter computer count (default: 0):", 0)
        resp = self._sendService("/Round/Create", requests.post, data={
            "Width": widthCount,
            "Height": heightCount,
            "MineCount": mineCount,
            "PlayerCount": playerCount,
            "ComputerCount": computerCount
        })
        if resp["Code"] >= 0:
            self._joinedRoundId = resp["RoundId"]
            print "RoundId:{}".format(self._joinedRoundId)

        return False if resp is None else resp["Code"] >= 0

    def _joinGame(self, allIds):
        while True:
            roundId = self._view.GetPlayerAnswer("Please enter game id (-1 will left join):")
            if roundId == -1:
                return False
            elif roundId in allIds:
                break
            print "Please enter valid game id."
        resp = self._sendService("/Round/Join", requests.post, data={
            "RoundId": roundId
        })

        if resp["Code"] >= 0:
            self._joinedRoundId = resp["RoundId"]

        return False if resp is None else resp["Code"] >= 0

    def _leftGame(self):
        resp = self._sendService("/Round/Leave", requests.post)

        return False if resp is None else resp["Code"] >= 0

    def _sendService(self, url, method, data=None, useAuth=True, printLog=True):
        headers = {}
        if useAuth:
            headers["Authorization"] = self._token

        keyStr = ""
        if data is not None:
            dataDict = json.loads(json.dumps(data))
            keys = [k for k in dataDict.keys()]
            keys.sort(key=lambda k: k)
            for key in keys:
                keyStr += "{}={}&".format(key, dataDict[key])

        hashAlgo = md5()
        hashAlgo.update(keyStr)
        headers["CheckSum"] = hashAlgo.hexdigest()
        headers["content-Type"] = "application/json"
        try:
            # data for post, params for get
            resp = method(Client.ServerUrl + url, data=json.dumps(data), params=data, headers=headers)
            if len(resp.content) == 0:
                print "Send service error. State:{}".format(resp.status_code)
                return None
            content = resp.json()
            code = content["Code"]
            if code == 0:
                if printLog:
                    print "{} Success".format(url.replace("/", ""))
            else:
                print self._codeDict[code]
                if code in [-105, -107, -108]:
                    print "Param: " + json.dumps(data)

            return content
        except ValueError:
            print "Error while sending to service: url:{} status:{}".format(url, resp.status_code)
