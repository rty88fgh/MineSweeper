from FileDao import FileDao


class AccountDao(object):
    def __init__(self):
        self._dao = FileDao()

    def CreateAccount(self, name, password):
        data = {
            "Name": name,
            "Password": password
        }

        return self._dao.Insert(name, data)

    def FindAccount(self, name):
        return self._dao.FindByKey(name)
