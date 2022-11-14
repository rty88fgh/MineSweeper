import hashlib

import jwt

from AccountDAOFile import AccountDAOFile


class AccountManager(object):
    SECRET_KEY = "IGS"

    def __init__(self):
        self._dao = AccountDAOFile()
        self._tokens = []

    def Login(self, name, password):
        account = self._dao.FindByName(name)
        return not (account is None or account["Password"] != password)

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

        self._dao.Insert(name, password)
        return True

