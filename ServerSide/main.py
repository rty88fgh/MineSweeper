import waitress as waitress
from gevent import monkey
from AccountManager import AccountManager
from Dispatcher import Dispatcher
from RoundManager import RoundManager

monkey.patch_all()

if __name__ == "__main__":
    dispatcher = Dispatcher()
    accountManager = AccountManager(dispatcher.Register)
    roundManager = RoundManager(accountManager, dispatcher.Register)
    dispatcher.SetAccountManager(accountManager)

    waitress.serve(dispatcher.Api, host='0.0.0.0', port='6060')

