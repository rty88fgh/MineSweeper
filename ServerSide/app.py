import falcon as falcon
from Game import Game

game = Game()
app = application = falcon.API()
app.add_route("/Login", game, suffix="Login")
app.add_route("/ConfigGame", game, suffix="ConfigGame")
app.add_route("/Start", game, suffix="Start")
app.add_route("/Action", game, suffix="Action")
app.add_route("/GameInfo", game, suffix="GameInfo")
app.add_route("/Replay", game, suffix="Replay")
app.add_route("/InitGame", game, suffix="InitGame")
app.add_route("/Register", game, suffix="Register")
