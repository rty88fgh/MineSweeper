from abc import ABCMeta, abstractmethod


class ManagerBase:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.AllProcessMethod = {}

    @abstractmethod
    def Process(self, funcName, **kwargs):
        pass

    def GetAllProcessInfo(self):
        result = []
        for info in self.AllProcessMethod.values():
            result.append({k: v for k, v in info.items() if not k.startswith('_')})
        return result

    def RegisterProcessMethod(self, name, method, func, useAuth=True):
        self.AllProcessMethod[name] = {
            'Name': name,
            'Method': method,
            'UseAuth': useAuth,
            '_func': func
        }
