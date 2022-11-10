import falcon as falcon

from Dispatcher import Dispatcher

dispatcher = Dispatcher()
app = application = falcon.API()
app.add_route("/Login", dispatcher, suffix="Login")
app.add_route("/Create", dispatcher, suffix="Create")
app.add_route("/GetAllRound", dispatcher, suffix="GetAllRound")
app.add_route("/Join", dispatcher, suffix="Join")
app.add_route("/Leave", dispatcher, suffix="Leave")
app.add_route("/GetJoinedRound", dispatcher, suffix="GetJoinedRound")
app.add_route("/Open", dispatcher, suffix="Open")
app.add_route("/SetFlag", dispatcher, suffix="SetFlag")
app.add_route("/Surrender", dispatcher, suffix="Surrender")
app.add_route("/Register", dispatcher, suffix="Register")
