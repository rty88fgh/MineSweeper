import json
from IDAO import IDao


class AccountDao(IDao):
    PLAYER_INFO_FILE = "Account.json"

    def Insert(self, name, password):
        accounts = json.load(open(AccountDao.PLAYER_INFO_FILE, "r"))
        account = self.FindByName(name)
        if account is not None:
            return None
        account = {
            "Name": name,
            "Password": password,
        }
        accounts.append(account)
        fp = open(AccountDao.PLAYER_INFO_FILE, "w+")
        fp.write(json.dumps(accounts))
        return account

    def FindAll(self):
        return json.load(open(AccountDao.PLAYER_INFO_FILE, "r"))

    def FindByName(self, name):
        accounts = json.load(open(AccountDao.PLAYER_INFO_FILE, "r"))
        return next((a for a in accounts if a["Name"] == name), None)

    def DeleteByName(self, name):
        accounts = json.load(open(AccountDao.PLAYER_INFO_FILE, "r"))
        account = next((a for a in accounts if a["name"] == name), None)
        if account is None:
            return None
        del accounts[account]
        fp = open(AccountDao.PLAYER_INFO_FILE, "w+")
        fp.write(json.dumps(accounts))
        return account
