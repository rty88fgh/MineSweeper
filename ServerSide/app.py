import falcon as falcon
from Game import Game

game = Game()
app = application = falcon.API()
app.add_route("/Login", game, suffix="Login")
app.add_route("/ConfigGame", game, suffix="ConfigGame")
app.add_route("/Start", game, suffix="Start")
app.add_route("/Click", game, suffix="Click")
app.add_route("/Flag", game, suffix="Flag")
app.add_route("/GetGameInfo", game, suffix="GetGameInfo")
app.add_route("/Replay", game, suffix="Replay")
app.add_route("/Register", game, suffix="Register")
