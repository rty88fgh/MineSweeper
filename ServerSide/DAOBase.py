from abc import ABCMeta, abstractmethod


class DAOBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def Insert(self, **kwargs):
        pass

    @abstractmethod
    def FindAll(self):
        pass

    @abstractmethod
    def FindByName(self, **kwargs):
        pass


