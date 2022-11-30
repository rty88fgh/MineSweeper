from pymongo import MongoClient
from IDao import IDao


class DbDao(IDao):

    def __init__(self, database, collection):
        self._client = MongoClient("localhost", 27017, maxPoolSize=10)
        self._db = database
        self._collection = collection

    def Delete(self, key, **kwargs):
        result = self._getDbCollection(**kwargs).delete_one(self._generateKey(key))
        return result.deleted_count == 1

    def Find(self, key, **kwargs):
        return self._getDbCollection(**kwargs).find_one(self._generateKey(key))

    def FindAll(self, filterFunc=None, **kwargs):
        filterObj = kwargs.get("filterObj", {})
        result = self._getDbCollection(**kwargs).find(filterObj)
        return result if filterFunc is None else [r for r in result if filterFunc(r)]

    def Insert(self, data, **kwargs):
        return self._getDbCollection(**kwargs).insert_one(data).inserted_id is not None

    def Update(self, key, data, **kwargs):
        isReplace = kwargs.get("isReplace", False)
        updateData = data if isReplace else {"$set": data}
        result = self._getDbCollection(**kwargs).update_one(self._generateKey(key), updateData)
        return result.modified_count > 0

    def _generateKey(self, value):
        return {} if value is None else {"Name": value}

    def _getDbCollection(self, **kwargs):
        return self._client[kwargs.get("db", self._db)][kwargs.get("collection", self._collection)]
