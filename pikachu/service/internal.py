# -*- coding: utf-8 -*-
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from twisted.python.failure import Failure

from pikachu.backend.wechat import WeChatSDK
from pikachu import json_encode

class InternalService(Resource):
    isLeaf = False
    serviceName = 'internal'

    def __init__(self, c, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.config = c

    def render_GET(self, request):
        request.setResponseCode(403)
        request.write("You can NOT visit this service!")
        request.finish()
        return NOT_DONE_YET

class AccessTokenService(Resource):
    isLeaf = True
    serviceName = "get_access_token"

    def __init__(self, c, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.config = c

    def finish(self, value, request):
        #request.setHeader('Content-Type', 'application/xhtml+xml; charset=UTF-8')
        #request.setHeader('Content-Type', 'text/html; charset=UTF-8')
        request.setHeader('Content-Type', 'application/json; charset=UTF-8')
        if isinstance(value, Failure):
            value.printTraceback()
            err = value.value
            request.setResponseCode(500)
            error = str(err)
            request.write(error + "\n")
        else:
            request.setResponseCode(200)
            request.write(json_encode(value) + "\n")
        request.finish()

    def cancel(self, err, call):
        call.cancel()

    def render_GET(self, request):
        wechat = WeChatSDK()
        d = wechat.getAccessToken()
        d.addBoth(self.finish, request)
        return NOT_DONE_YET
