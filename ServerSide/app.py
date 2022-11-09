import falcon as falcon
from GameManager import GameManager

gameManager = GameManager()
app = application = falcon.API()
app.add_route("/Login", gameManager, suffix="Login")
app.add_route("/CreateNewGame", gameManager, suffix="CreateNewGame")
app.add_route("/GetInfo", gameManager, suffix="GetInfo")
app.add_route("/Join", gameManager, suffix="Join")
app.add_route("/Leave", gameManager, suffix="Leave")
app.add_route("/GetDetail", gameManager, suffix="GetDetail")
app.add_route("/Click", gameManager, suffix="Click")
app.add_route("/Flag", gameManager, suffix="Flag")
app.add_route("/Surrender", gameManager, suffix="Surrender")
app.add_route("/Register", gameManager, suffix="Register")
