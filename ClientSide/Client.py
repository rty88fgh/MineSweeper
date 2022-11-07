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
            gameInfo = json.loads(
                requests.get(Client.ServerUrl + "/GetGameInfo", headers={"Authorization": self._token}).json())
            if gameInfo["Status"] == "Playing":
                break
            else:
                gevent.sleep(1)
                continue

        self._view.InitPyGame(gameInfo["Width"], gameInfo["Height"], self._playerName)
        while not gameInfo["Status"] == "EndGame":
            info = self._getRefreshViewParams()

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
            elif action == View.Replay:
                requests.post(Client.ServerUrl + "/Replay", {}, headers={"Authorization": self._token})
                continue

            requests.post("{}/{}".format(Client.ServerUrl, action), json.dumps({
                "X": pos[0],
                "Y": pos[1],
            }), headers={"Authorization": self._token})

    def _convertBool(self, value):
        if str(value).lower() in ["y", "yes"]:
            return True
        elif str(value).lower() in ["n", "no"]:
            return False
        else:
            raise ValueError()

    def _getRefreshViewParams(self):
        return json.loads(requests.get(Client.ServerUrl + "/GetGameInfo", headers={"Authorization": self._token}).json())

    def _register(self):
        name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
        pwd = self._view.GetPlayerAnswer("Password: ", isStr=True, defaultValue="1234")
        resp = json.loads(requests.post(Client.ServerUrl + "/Register", json.dumps({
            "Name": name,
            "Pwd": pwd
        })).json())

        if resp["IsSuccess"]:
            print "{} register successfully".format(name)
        else:
            print "Failed to register {}. Msg:{}".format(name, resp["Message"])

        return resp["IsSuccess"]

    def _login(self):
        name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
        pwd = self._view.GetPlayerAnswer("Password: ", isStr=True, defaultValue="1234")
        resp = requests.post(Client.ServerUrl + "/Login", json.dumps({
            "Name": name,
            "Pwd": pwd
        }))
        result = json.loads(resp.json()) if len(resp.content) > 0 else {}
        msg = result.get("Message", None)
        isSuccess = bool(result.get("IsSuccess", False))
        if resp.status_code == 200:
            if not isSuccess:
                print "Failed to login. Msg:{}".format(msg)
                return
            else:
                if msg is not None:
                    print msg

                self._playerName = name
                print "{} join success".format(name)
                self._token = result.get("Token")
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
            "Width": widthCount,
            "Height": heightCount,
            "MineCount": mineCount,
            "ComputerCount": computerCount
        }), headers={"Authorization": self._token})


        self._view.GetPlayerAnswer("It will start game when click enter...", isStr=True, defaultValue="")
        resp = json.loads(
            requests.post(Client.ServerUrl + "/Start", {}, headers={"Authorization": self._token}).json())
        if not resp["IsSuccess"]:
            print resp["Message"]

        return resp["IsSuccess"]
