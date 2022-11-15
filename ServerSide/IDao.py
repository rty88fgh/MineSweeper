from abc import ABCMeta, abstractmethod


class IDao:
    __metaclass__ = ABCMeta

    @abstractmethod
    def Insert(self, name, password):
        pass

    @abstractmethod
    def FindAll(self):
        pass

    @abstractmethod
    def FindByName(self, name):
        pass

    @abstractmethod
    def DeleteByName(self, name):
        pass


