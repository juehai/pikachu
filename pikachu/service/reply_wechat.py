# -*- coding: utf-8 -*-
# Author: Yang Gao<gaoyang.public@gmail.com>

from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from twisted.internet.threads import deferToThread
from twisted.python.failure import Failure

from pikachu.log import *
from pikachu.backend.wechat import WeChatSDK, WeChatValidateError

class ReplyWeChatService(Resource):
    isLeaf = True
    serviceName = "reply_wechat"

    def __init__(self, c, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.config = c

    def parese(self, request):
        request.content.seek(0, 0)
        content = request.content.read()
        debug("content size = %d" % len(content))
        if content:
            return defer.succeed(WeChatSDK.parse(content))
        else:
            return defer.succeed(None)

    def finish(self, value, request):
        #request.setHeader('Content-Type', 'application/xhtml+xml; charset=UTF-8')
        request.setHeader('Content-Type', 'text/html; charset=UTF-8')
        if isinstance(value, Failure):
            err = value.value
            request.setResponseCode(500)
            if isinstance(err, WeChatValidateError):
                request.setResponseCode(400)
                request.write('Signature validate failed.')
            else:
                error = str(err)
                request.write(error + "\n")
        else:
            request.setResponseCode(200)
            request.write("%s\n" % value)
        request.finish()

    @defer.inlineCallbacks
    def reply(self, res, request):
        msg_type = res.get('mtype', '').lower()
        if msg_type == 'event':
            pass
        else:
            content = res.get('content', '')
        defer.returnValue(content)

    def cancel(self, err, call):
        call.cancel()

    def render_GET(self, request):
        signature = request.args.get('signature', '')
        timestamp  = request.args.get('timestamp', '')
        nonce  = request.args.get('nonce', '')
        wechat = WeChatSDK()
        if not wechat.validate(signature, timestamp, nonce):
            error_message = "sign: %s, timestamp: %s, nonce: %s" % (signature,
                                                                   timestamp,
                                                                   nonce)
            raise WeChatValidateError(error_message)

        d = self.parse(request)
        request.notifyFinish().addErrback(self.cancel, d)
        d.addCallback(self.reply, request)
        d.addBoth(self.finish, request)
        return NOT_DONE_YET
