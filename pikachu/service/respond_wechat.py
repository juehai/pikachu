# -*- coding: utf-8 -*-
# Author: Yang Gao<gaoyang.public@gmail.com>

from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from twisted.python.failure import Failure

from pikachu.log import *
from pikachu.backend.wechat import WeChatSDK
from pikachu.backend.wechat import WeChatValidateError
from pikachu.backend.wechat import WeChatReply
from pikachu.action.wechatbot import WeChatBot 

class RespondWeChatService(Resource):
    isLeaf = True
    serviceName = "respond_wechat"

    def __init__(self, c, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.config = c

    def parse(self, request):
        request.content.seek(0, 0)
        content = request.content.read()
        debug("content size = %d" % len(content))
        if content:
            return defer.succeed(WeChatSDK.parse(content))
        else:
            return defer.succeed(None)

    def finish(self, value, request):
        #request.setHeader('Content-Type', 'application/xhtml+xml; charset=UTF-8')
        request.setHeader('Content-Type', 'text/xml; charset=UTF-8')
        if isinstance(value, Failure):
            err = value.value
            request.setResponseCode(500)
            if isinstance(err, WeChatValidateError):
                request.setResponseCode(400)
                request.write('Signature validate failed.')
            else:
                err_msg = str(err)
                error('v'*50)
                value.printTraceback()
                error('^'*50)
                request.write(err_msg + "\n")
        else:
            request.setResponseCode(200)
            debug("value type: %s" % type(value))
            debug(value)
            request.write(value.encode('utf-8'))
        request.finish()

    def respond(self, res, request):
        robot = Talkbot()
        content = robot.reflect(**res)
        return content

    def cancel(self, err, call):
        call.cancel()

    def render_GET(self, request):
        echostr = request.args.get('echostr', [''])[0]
        d = self.parse(request)
        request.notifyFinish().addErrback(self.cancel, d)
        d.addCallback(lambda x: echostr)
        d.addBoth(self.finish, request)
        return NOT_DONE_YET

    def render_POST(self, request):
        # TODO: If message with Chinese, it always got a encode error
        # but I haven't found where got mistake.
        d = self.parse(request)
        request.notifyFinish().addErrback(self.cancel, d)
        d.addCallback(self.respond, request)
        d.addBoth(self.finish, request)
        return NOT_DONE_YET
