import os
import waitress as waitress
import app
from gevent import monkey

monkey.patch_all()

if __name__ == "__main__":
    waitress.serve(app.app, host='0.0.0.0', port='6060')