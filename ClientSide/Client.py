import json
from hashlib import md5

import gevent
import requests

from Code import Code
from View import View


class Client(object):
    ServerUrl = "http://127.0.0.1:6060"

    def __init__(self):
        self._view = View()
        self._playerName = ""
        self._lastUpdateTime = 0
        self._token = None
        self._codeDict = {
            Code.PARAMS_INVALID: "Enter name or password error",
            Code.PLAYER_DUPLICATE: "Player name is duplicate.",
            Code.HAVE_JOINED: "{} has joined".format(self._playerName),
            Code.PARAMS_INVALID: "Name or password error",
            Code.HAVE_JOINED: "{} cannot create round while has joined othrer round".format(self._playerName),
            Code.PARAMS_INVALID: "Parameter error",
            Code.ROUNDID_NOT_FIND: "RoundId:{} did not found.",
            Code.HAVE_JOINED: "{} has joined other game.",
            Code.ROUND_NOT_INIT: "RoundId:{} status isn't Init",
            Code.JOIN_BACK: "{} joined back".format(self._playerName),
            Code.PLAYER_NOT_JOIN: "{} did not join round".format(self._playerName),
            Code.POSITION_INVALID: "Position error",
            Code.LOGIN_FAILED: "Login Failed"
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
            resp = self._sendService("/GetAllRound", requests.get)

            if resp is None:
                print "Failed to get all rounds. It will retry 1 sec..."
                gevent.sleep(1)
                continue

            roundsInfo = resp["data"]

            print "Rounds:"
            for info in roundsInfo:
                players = info["Players"]
                print "Round Id:{} Status:{} Players:{}".format(
                    info["RoundId"],
                    info["Status"],
                    "".join(
                        [p["Name"] + "," if p["Name"] != players[len(players) - 1] else p["Name"] for p in players]))

            menuAns = self._view.ConsoleMenu(["Create new game", "Join", "Left"])
            if menuAns == 0 and self._createGame():
                break
            elif menuAns == 1 and self._joinGame([i["RoundId"] for i in roundsInfo]):
                break
            elif menuAns == 2:
                self._leftGame()

        print "Waiting for start..."

        isInit = False
        while True:
            resp = self._sendService("/GetJoinedRound", requests.get, printLog=False)

            if resp is None:
                print "Failed to get joined round. It will retry 1 sec..."
                gevent.sleep(1)
                continue
            info = resp["data"]
            if info["Status"] == "Init":
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
                self._sendService("/Surrender", requests.post, )
                continue

            self._sendService("/" + action, requests.post, data={
                "X": pos[0],
                "Y": pos[1],
            }, printLog=False)

    def _register(self):
        name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
        password = self._view.GetPlayerAnswer("Password: ", isStr=True, defaultValue="1234")
        resp = self._sendService("/Register", requests.post, data={
            "Name": name,
            "Password": password
        }, useAuth=False)

        if resp is None:
            return False

        return self._login(name=name, password=password) if resp["Code"] >= 0 else False

    def _login(self, name=None, password=None):
        if name is None:
            name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
        if password is None:
            password = self._view.GetPlayerAnswer("Password: ", isStr=True, defaultValue="1234")

        resp = self._sendService("/Login", requests.post, data={
            "Name": name,
            "Password": password
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
        resp = self._sendService("/Create", requests.post, data={
            "Width": widthCount,
            "Height": heightCount,
            "MineCount": mineCount,
            "PlayerCount": playerCount,
            "ComputerCount": computerCount
        })
        if resp["Code"] >= 0:
            print "RoundId:{}".format(resp["RoundId"])

        return False if resp is None else resp["Code"] >= 0

    def _joinGame(self, allIds):
        while True:
            roundId = self._view.GetPlayerAnswer("Please enter game id (-1 will left join):")
            if roundId == -1:
                return False
            elif roundId in allIds:
                break
            print "Please enter valid game id."
        resp = self._sendService("/Join", requests.post, data={
            "RoundId": roundId
        })

        return False if resp is None else resp["Code"] >= 0

    def _leftGame(self):
        resp = self._sendService("/Leave")

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
            resp = method(Client.ServerUrl + url, data=json.dumps(data), headers=headers)
            if len(resp.content) == 0:
                print "Send service error. Status:{}".format(resp.status_code)
                return None
            content = resp.json()
            code = content["Code"]
            if code == Code.SUCCESS:
                if printLog:
                    print "{} Success".format(url.replace("/", ""))
            else:
                print self._codeDict[code]
                if code in [Code.PARAMS_INVALID, Code.POSITION_INVALID, Code.ACTION_INVALID]:
                    print "Param: " + json.dumps(data)

            return content
        except ValueError:
            print "Error while sending to service: url:{} status:{}".format(url, resp.status_code)
