import hashlib

import jwt

from AccountDAOFile import AccountDAOFile
from Code import Code


class AccountManager(object):
    SECRET_KEY = "IGS"

    def __init__(self):
        self._dao = AccountDAOFile()
        self._tokens = []

    def Login(self, name, password):
        account = self._dao.FindByName(name)
        algo = hashlib.md5()
        algo.update(password)
        return not (account is None or account["Password"] != algo.hexdigest())

    def EncodeToken(self, name):
        token = jwt.encode({
            "Name": name,
        }, AccountManager.SECRET_KEY)
        self._tokens.append(token)
        return token

    def DecodeToken(self, token):
        try:
            if token not in self._tokens:
                return None
            return jwt.decode(token, key=AccountManager.SECRET_KEY)
        except:
            return None

    def Create(self, name, password):
        player = self._dao.FindByName(name)
        if player is not None:
            return False

        hashAlgo = hashlib.md5()
        hashAlgo.update(password)
        self._dao.Insert(name, hashAlgo.hexdigest())
        return True

