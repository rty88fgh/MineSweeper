from abc import ABCMeta, abstractmethod


class IDao:
    __metaclass__ = ABCMeta

    @abstractmethod
    def Insert(self, key, data, force=False):
        pass

    @abstractmethod
    def FindAll(self, filterFunc=None):
        pass

    @abstractmethod
    def Find(self, key):
        pass

    @abstractmethod
    def Delete(self, key):
        pass


