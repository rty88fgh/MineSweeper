import json
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

    def Run(self):
        while True:
            print "===================="
            menuAns = self._view.ConsoleMenu(["Register", "Login"])
            if menuAns == 0:
                self._register()
            elif menuAns == 1 and self._login():
                break

        while True:
            gamesInfo = requests.get(Client.ServerUrl + "/GetAllGamesInfo",
                                     headers={"Authorization": self._token}).json()
            print "Games:"
            for info in gamesInfo:
                players = info["Players"]
                print "Game Id:{} Status:{} Players:{}".format(
                    info["GameId"],
                    info["Status"],
                    "".join([name + "," if name != players[len(players) - 1] else name for name in players]))
            menuAns = self._view.ConsoleMenu(["Create new game", "Join", "Left"])
            if menuAns == 0 and self._configGame():
                break
            elif menuAns == 1 and self._joinGame():
                break
            elif menuAns == 2:
                self._leftGame()

        print "Waiting for start..."
        while True:
            gameInfo = requests.get(Client.ServerUrl + "/GetGameDetail", headers={"Authorization": self._token}).json()
            if gameInfo["Status"] != "Init":
                break
            else:
                gevent.sleep(1)
                continue

        self._view.InitPyGame(gameInfo["Width"], gameInfo["Height"], self._playerName)
        while True:
            info = requests.get(Client.ServerUrl + "/GetGameDetail", headers={"Authorization": self._token}).json()

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
                requests.post(Client.ServerUrl + "/Surrender", {}, headers={"Authorization": self._token})
                continue

            requests.post("{}/{}".format(Client.ServerUrl, action), json.dumps({
                "X": pos[0],
                "Y": pos[1],
            }), headers={"Authorization": self._token})

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
        result = resp.json() if len(resp.content) > 0 else {}
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
        widthCount = self._view.GetPlayerAnswer("Please enter width count (5 ~ 20, default: 10):", 10)
        heightCount = self._view.GetPlayerAnswer("Please enter height count (5 ~ 20, default: 10):", 10)
        mineCount = self._view.GetPlayerAnswer("Please enter mine count (1 ~ 20, default: 9):", 9)
        playerCount = self._view.GetPlayerAnswer("Please enter player count (default: 2):", 2)
        computerCount = self._view.GetPlayerAnswer("Please enter computer count (default: 0):", 0)
        resp = requests.post(Client.ServerUrl + "/CreateNewGame", json.dumps({
            "Width": widthCount,
            "Height": heightCount,
            "MineCount": mineCount,
            "PlayerCount": playerCount,
            "ComputerCount": computerCount
        }), headers={"Authorization": self._token}).json()

        if not resp["IsSuccess"]:
            print "Error: " + resp["Message"]
            return False

        print "Game id:{}".format(resp["GameId"])
        return resp["IsSuccess"]

    def _joinGame(self):
        while True:
            gameId = self._view.GetPlayerAnswer("Please enter game id (-1 will left join):")
            if gameId in [g["GameId"] for g in gamesInfo]:
                break
            elif gameId == -1:
                return False
            print "Please enter valid game id."

        joinResp = requests.post(Client.ServerUrl + "/JoinGame", json.dumps({
                "id": gameId
            }), headers={"Authorization": self._token}).json()

        print ("Error:" + joinResp["Message"]) if not joinResp["IsSuccess"] else "Join gameId:{} Success".format(gameId)
        return joinResp["IsSuccess"]

    def _leftGame(self):
        joinResp = requests.post(Client.ServerUrl + "/LeaveGame", headers={"Authorization": self._token}).json()

        print ("Error:" + joinResp["Message"]) if not joinResp["IsSuccess"] else \
            "{} lefts gameId:{} Success".format(self._playerName, joinResp["GameId"])
        return joinResp["IsSuccess"]
