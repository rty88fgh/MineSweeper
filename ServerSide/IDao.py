from abc import ABCMeta, abstractmethod


class IDao:
    __metaclass__ = ABCMeta

    @abstractmethod
    def Insert(self, data, **kwargs):
        pass

    @abstractmethod
    def FindAll(self, filterFunc=None, **kwargs):
        pass

    @abstractmethod
    def Find(self, key, **kwargs):
        pass

    @abstractmethod
    def Delete(self, key, **kwargs):
        pass

    @abstractmethod
    def Update(self, key, data, **kwargs):
        pass



