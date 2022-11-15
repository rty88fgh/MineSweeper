import falcon
from hashlib import md5


class Dispatcher(object):
    def __init__(self, _isValidTokenFunc, *managers):
        self.Api = falcon.API()
        self._managers = {}
        self._registerAPI(managers)
        self._isValidTokenFunc = _isValidTokenFunc

    def on_get(self, req, resp):
        self._processClientRequest(req, resp, 'Get')

    def on_post(self, req, resp):
        self._processClientRequest(req, resp, 'Post')

    def _processClientRequest(self, req, resp, method):
        splits = req.path.replace('/', '').split('_')
        if splits[0] not in self._managers.keys():
            resp.status = 404
            return

        manager = self._managers[splits[0]]
        funcInfo = next((info for info in manager.GetAllProcessInfo() if info['Name'] == splits[1]), None)
        if funcInfo is None:
            resp.status = falcon.HTTP_NOT_FOUND
            return

        if funcInfo['Method'] != method:
            resp.status = falcon.HTTP_METHOD_NOT_ALLOWED
            return

        if not self._isValidRequest(req):
            resp.status = falcon.HTTP_UNAUTHORIZED
            return

        token = None
        if funcInfo['UseAuth']:
            token = req.headers.get("Authorization".upper(), None)
            if token is None or not self._isValidTokenFunc(token):
                resp.status = falcon.HTTP_UNAUTHORIZED
                return

        code, returnValues = manager.Process(Token=token,
                                             FuncName=funcInfo['Name'],
                                             **({} if req.media is None else req.media))

        self._setRespMsg(resp, code, **({} if returnValues is None else returnValues))

    def _registerAPI(self, managers):
        for g in managers:
            name = type(g).__name__.replace('Manager', '')

            for info in g.GetAllProcessInfo():
                self.Api.add_route("/{}_{}".format(name, info['Name']), self)
            self._managers[name] = g

    def _setRespMsg(self, resp, code, **kwargs):
        resp.status = falcon.HTTP_OK
        resp.headers["Content-type"] = "application/json"
        rtn = {
            "Code": code,
        }
        for k, v in kwargs.items():
            rtn[k] = v

        resp.media = rtn

    def _isValidRequest(self, req):
        checkSum = req.headers.get("CheckSum".upper(), None)
        if checkSum is None:
            return False

        keyStr = ""
        if req.media is not None:
            sortKey = [k for k in req.media.keys()]
            sortKey.sort(key=lambda key: key)
            for k in sortKey:
                keyStr += "{}={}&".format(k, req.media[k])

        hashAlgo = md5()
        hashAlgo.update(keyStr)
        return hashAlgo.hexdigest() == checkSum
