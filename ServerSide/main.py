import waitress as waitress
from gevent import monkey
from AccountManager import AccountManager
from Dispatcher import Dispatcher
from RoundManager import RoundManager

monkey.patch_all()

if __name__ == "__main__":
    accountManager = AccountManager()
    roundManager = RoundManager(accountManager)
    dispatcher = Dispatcher(accountManager.IsValidToken,
                            accountManager,
                            roundManager)
    waitress.serve(dispatcher.Api, host='0.0.0.0', port='6060')