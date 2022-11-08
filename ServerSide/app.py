import falcon as falcon
from GameManager import GameManager

gameManager = GameManager()
app = application = falcon.API()
app.add_route("/Login", gameManager, suffix="Login")
app.add_route("/CreateNewGame", gameManager, suffix="CreateNewGame")
app.add_route("/GetAllGamesInfo", gameManager, suffix="GetAllGamesInfo")
app.add_route("/JoinGame", gameManager, suffix="JoinGame")
app.add_route("/LeftGame", gameManager, suffix="LeftGame")
app.add_route("/GetGameDetail", gameManager, suffix="GetGameDetail")
app.add_route("/Click", gameManager, suffix="Click")
app.add_route("/Flag", gameManager, suffix="Flag")
app.add_route("/Surrender", gameManager, suffix="Surrender")
app.add_route("/Register", gameManager, suffix="Register")
