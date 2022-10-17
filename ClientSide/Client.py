import json
import string

import gevent
import requests
from gevent import monkey
from View import View


class Client(object):
    ServerUrl = "http://127.0.0.1:8080"

    def __init__(self):
        self._view = View()
        self._playerName = ""
        self._lastUpdateTime = 0

    def Run(self):
        # monkey.patch_all()
        while True:
            name = self._view.GetPlayerAnswer("What's your name?", isStr=True, defaultValue="Terry")
            resp = requests.post(Client.ServerUrl + "/Join", json.dumps({"name": name}))
            if resp.status_code == 200:
                msg = json.loads(resp.json()).get("message", None) if len(resp.content) != 0 else None
                if msg is not None:
                    print msg
                self._playerName = name
                break
            print "{} cannot find in players".format(name)

        isMaster = self._view.GetPlayerAnswer("Are you master?", False, convertFunc=self.ConvertBool)
        if not isMaster:
            print "Waiting for start..."
            while True:
                gameInfo = json.loads(requests.get(Client.ServerUrl + "/GameInfo").json())
                if gameInfo["status"] == "Playing":
                    break
                else:
                    gevent.sleep(1)
                    continue
        else:
            width_count = self._view.GetPlayerAnswer("Please enter width count (default: 10):", 10)
            height_count = self._view.GetPlayerAnswer("Please enter height count (default: 10):", 10)
            mine_count = self._view.GetPlayerAnswer("Please enter mine count (default: 9):", 9)
            requests.post(Client.ServerUrl + "/ConfigGame", json.dumps({
                "width": width_count,
                "height": height_count,
                "mineCount": mine_count
            }))
            self._view.GetPlayerAnswer("It will start game when click enter...", isStr=True, defaultValue="")
            resp = json.loads(requests.get(Client.ServerUrl + "/Start", {}).json())
            if not resp["isSuccess"]:
                print resp["message"]
                return

        gameInfo = json.loads(requests.get(Client.ServerUrl + "/GameInfo").json())
        self._view.InitPyGame(gameInfo["width"], gameInfo["height"], self._playerName)
        while not gameInfo["status"] == "EndGame":

            info = self.GetRefreshViewParams()

            if info["lastUpdateTime"] != self._lastUpdateTime:
                self._view.RefreshView(info["grids"],
                                       info["players"],
                                       info["current"],
                                       info["scoreMsg"],
                                       info["winner"])
                self._lastUpdateTime = info["lastUpdateTime"]
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
                requests.post(Client.ServerUrl + "/Replay", {})
                continue

            requests.post(Client.ServerUrl + "/Action", json.dumps({
                "action": action,
                "x": pos[0],
                "y": pos[1],
                "name": self._playerName,
            }))

    def ConvertBool(self, value):
        if str(value).lower() in ["y", "yes"]:
            return True
        elif str(value).lower() in ["n", "no"]:
            return False
        else:
            raise ValueError()

    def SendServer(self, url, content, func, **kwargs):
        return json.loads(func(Client.ServerUrl + url, json.dumps(content), kwargs).json())

    def GetRefreshViewParams(self):
        return json.loads(requests.get(Client.ServerUrl + "/GameInfo").json())
