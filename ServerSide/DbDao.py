from pymongo import MongoClient


class DbDao(object):

    def __init__(self, database, collection):
        self._client = MongoClient("localhost", 27017, maxPoolSize=10)
        self._db = database
        self._collection = collection

    def Delete(self, key, **kwargs):
        result = self._getDbCollection(**kwargs).delete_one(key)
        return result.deleted_count == 1

    def Find(self, key, sort=None, projection=None, **kwargs):
        query = self._getDbCollection(**kwargs)
        return query.find_one(key, sort=sort, projection=projection)

    def FindAll(self, find, sort=None, projection=None, **kwargs):
        query = self._getDbCollection(**kwargs)
        return query.find(find, sort=sort, projection=projection)

    def Insert(self, data, **kwargs):
        return self._getDbCollection(**kwargs).insert_one(data).inserted_id is not None

    def Update(self, key, data, isReplace=False, **kwargs):
        updateData = data if isReplace else {"$set": data}
        result = self._getDbCollection(**kwargs).update_one(key, updateData)
        return result.modified_count > 0

    def _getDbCollection(self, **kwargs):
        return self._client[kwargs.get("db", self._db)][kwargs.get("collection", self._collection)]
