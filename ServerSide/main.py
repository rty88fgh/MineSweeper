import os

import waitress as waitress

import app

if __name__ == "__main__":
    waitress.serve(app.app, host=os.getenv('127.0.0.1', '0.0.0.0'), port=os.getenv('127.0.0.1', '8080'))