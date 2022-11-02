import json
import gevent
import requests
from View import View
import hashlib


class Client(object):
    ServerUrl = "http://127.0.0.1:6060"

    def __init__(self):
        self._view = View()
        self._playerName = ""
        self._lastUpdateTime = 0
        self._token = None
        self._hashAlgo = hashlib.md5()

    def Run(self):
        while True:
            print "===================="
            menuAns = self._view.ConsoleMenu(["Register", "Login"])
            if menuAns == 0:
                self._register()
            elif menuAns == 1 and self._login():
                break

        isMaster = self._view.GetPlayerAnswer("Are you master?", False, convertFunc=self._convertBool)
        if isMaster:
            if not self._configGame():
                return

        print "Waiting for start..."
        while True:
            gameInfo = json.loads(requests.get(Client.ServerUrl + "/GameInfo").json())
            if gameInfo["status"] == "Playing":
                break
            else:
                gevent.sleep(1)
                continue

        self._view.InitPyGame(gameInfo["width"], gameInfo["height"], self._playerName)
        while not gameInfo["status"] == "EndGame":
            info = self._getRefreshViewParams()

            if info["lastUpdateTime"] != self._lastUpdateTime:
                self._view.RefreshView(info["grids"],
                                       info["players"],
                                       info["current"],
                                       info["scoreMsg"],
                                       info["winner"])
                self._lastUpdateTime = info["lastUpdateTime"]
                gevent.sleep(1)
                continue
            else:
                result = self._view.GeActionPosition()
                if result is None:
                    continue
                action, pos = result

            if action == View.Quit:
                self._view.CloseWindows()
                return
            elif action == View.Replay:
                requests.post(Client.ServerUrl + "/Replay", {}, headers={"Authorization": self._token})
                continue

            requests.post(Client.ServerUrl + "/Action", json.dumps({
                "action": action,
                "x": pos[0],
                "y": pos[1],
            }), headers={"Authorization": self._token})

    def _convertBool(self, value):
        if str(value).lower() in ["y", "yes"]:
            return True
        elif str(value).lower() in ["n", "no"]:
            return False
        else:
            raise ValueError()

    def _getRefreshViewParams(self):
        return json.loads(requests.get(Client.ServerUrl + "/GameInfo").json())

    def _register(self):
        name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
        pwd = self._view.GetPlayerAnswer("Password: ", isStr=True, defaultValue="1234")
        self._hashAlgo.update(pwd)
        resp = json.loads(requests.post(Client.ServerUrl + "/Register", json.dumps({
            "name": name,
            "pwd": self._hashAlgo.hexdigest()
        })).json())

        if resp["isSuccess"]:
            print "{} register successfully".format(name)
        else:
            print "Failed to register {}. Msg:{}".format(name, resp["message"])

        return resp["isSuccess"]

    def _login(self):
        name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
        pwd = self._view.GetPlayerAnswer("Password: ", isStr=True, defaultValue="1234")
        self._hashAlgo.update(pwd)
        resp = requests.post(Client.ServerUrl + "/Login", json.dumps({
            "name": name,
            "pwd": self._hashAlgo.hexdigest()
        }))
        result = json.loads(resp.json()) if len(resp.content) > 0 else {}
        msg = result.get("message", None)
        isSuccess = bool(result.get("isSuccess", False))
        if resp.status_code == 200:
            if not isSuccess:
                print "Failed to login. Msg:{}".format(msg)
                return
            else:
                if msg is not None:
                    print msg

                self._playerName = name
                print "{} join success".format(name)
                self._token = result.get("token")
                return True
        elif resp.status_code == 401:
            print "Failed to login. Please try again."
        elif resp.status_code == 500:
            print "Service has some error. Please try again"
        else:
            print "Something unknown happen.{}".format(resp.json() if len(resp.content) > 0 else "")

        return False

    def _configGame(self):
        widthCount = self._view.GetPlayerAnswer("Please enter width count (default: 10):", 10)
        heightCount = self._view.GetPlayerAnswer("Please enter height count (default: 10):", 10)
        mineCount = self._view.GetPlayerAnswer("Please enter mine count (default: 9):", 9)
        computerCount = self._view.GetPlayerAnswer("Please enter computer count (default: 0):", 0)
        requests.post(Client.ServerUrl + "/ConfigGame", json.dumps({
            "width": widthCount,
            "height": heightCount,
            "mineCount": mineCount,
            "computerCount": computerCount
        }), headers={"Authorization": self._token})
        self._view.GetPlayerAnswer("It will start game when click enter...", isStr=True, defaultValue="")
        resp = json.loads(
            requests.post(Client.ServerUrl + "/Start", {}, headers={"Authorization": self._token}).json())
        if not resp["isSuccess"]:
            print resp["message"]

        return resp["isSuccess"]
