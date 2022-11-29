import falcon
from hashlib import md5


class Dispatcher(object):
    def __init__(self):
        self.Api = falcon.API()
        self._managers = {}
        self._isValidTokenFunc = None
        self._apiInfo = {}

    def on_post(self, req, resp):
        funcInfo = self._getApiInfo(req.path)

        if funcInfo is None:
            resp.status = falcon.HTTP_NOT_FOUND
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

        code, outParam = funcInfo['Callback'](Token=token,
                                              Path=req.path,
                                              **({} if req.media is None else req.media))

        self._setRespMsg(resp, code, **({} if outParam is None else outParam))

    def SetAuthFunc(self, isValidTokenFunc):
        self._isValidTokenFunc = isValidTokenFunc

    def Register(self, path, callback, useAuth=True, namespace=None):
        url = ("/" + namespace if namespace is not None else "") + "/" + path
        if url in self._apiInfo.keys():
            print "{} has been register.".format(url)
            return False

        self.Api.add_route(url, self)
        self._setApiInfo(path, namespace, {
            'Callback': callback,
            'UseAuth': useAuth,
        })
        return True

    def _getApiInfo(self, url):
        hierarchyPath = url.split('/')

        path = "/" + hierarchyPath[len(hierarchyPath) - 1]
        namespace = url.replace(path, "")

        return self._apiInfo[namespace].get(path, None) if namespace in self._apiInfo else None

    def _setApiInfo(self, path, namespace, data):
        namespaceUrl = "/" + namespace
        pathUrl = "/" + path
        nsInfo = self._apiInfo.get(namespaceUrl if namespace is not None else "", {})
        nsInfo[pathUrl] = data
        self._apiInfo[namespaceUrl] = nsInfo

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
