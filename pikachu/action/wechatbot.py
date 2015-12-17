# -*- coding: utf-8 -*-
# Author: Yang Gao<gaoyang.public@gmail.com>
from twisted.internet import defer
from twisted.web.client import getPage
from twisted.python.failure import Failure
from pikachu.backend.wechat import WeChatSDK, WeChatReply
from pikachu.log import *
from ujson import decode as json_decode
import re

class WeChatBotRuntimeError(Exception):
    pass

class InvalidMsgType(WeChatBotRuntimeError):
    pass

class InvalidEventType(WeChatBotRuntimeError):
    pass

event_mapping = {
    "V1001_TRACKING": u" -请点击左侧键盘图片\n -直接输入运单号码\n -多个单号请用空格隔开\n -最多输入5个单号"

}

@defer.inlineCallbacks
def getZTOTracking(billcodes):
    zto_api = 'http://zto.co.nz/api/v1/tracking?billcode=%s'
    page = yield getPage(zto_api % ','.join(billcodes))
    res = json_decode(page)
    content = ''
    if res['data']:
#        debug(u'Tracking data: %s' % res['data'])
        for datum in res['data']:
            content = '%s\n%s\n' % (content, '-'*10)
            content = content + u'运单号: %s\n' % datum['billCode']
            trace = '\n'.join(map(lambda x: '%s %s %s'% (x['scanDate'], 
                            x['scanType'] ,x['desc']), datum['traces']))
            content = '%s\n%s\n' % (content, trace)
#    debug('ZTO Tracking return: %s' % content.encode('utf-8'))
#    debug('ZTO Tracking return type: %s' % type(content))

    defer.returnValue(content)


class WeChatBot(object):
    msg_type = ['text', 'image', 'news', 'event']
    event_type = ['click', 'subscribe' ]

    def __init__(self):
        sdk = WeChatSDK()
        d = sdk.getAccessToken()
        
        d.addCallback(self._set_access_token)

    def _set_access_token(self, token):
        if isinstance(token, Failure):
            raise
        debug('save Access Token: %s' % token)
        self.access_token = token

    def _get_common_info(self, **kw):
        info = dict(
            sender = kw.get('receiver', ''),
            receiver = kw.get('sender', ''),
            message = kw.get('content', '')
        )
        return info

    def reflect(self, **kw):
        mtype = kw.get('mtype', '')
        reflect_content = ''

        #if not mtype in self.msg_type:
        #    raise InvalidMsgType()

        answer_func = getattr(self, 'answer_%s' % mtype,
                              self._invalid_msg_type)

        if callable(answer_func):
            reflect_content = answer_func(**kw)
        return reflect_content

    def answer_event(self, **kw):
        event = kw.get('event', '').lower()
        answer = ''
        #if not event in self.event_type:
        #    raise InvalidEventType()

        event_func = getattr(self, '_event_%s' % event, self._invalid_event)
        debug('event_func type: %s %s' % (type(event_func), event_func))
        if callable(event_func):
            answer = event_func(**kw)
        return answer

    def _make_text_reply(self, content, sender='', receiver=''):
        reply = WeChatReply(
            sender=sender,
            receiver=receiver,
            mtype='text',
            content=content,
        )
        return reply.text_reply()

    def _make_transfer_reply(self, content, sender='', receiver=''):
        reply = WeChatReply(
            sender = sender,
            receiver=receiver,
            mtype='transfer_customer_service',
            content=content
        )
        return reply.transfer_customer_service()

    def answer_text(self, **kw):
        info = self._get_common_info(**kw)
        debug('received wechat info: %s' % info)
        # find the 6 and 12 bits numbers in the message.
        re_express_billcodes = re.compile(r'(?<!\d)(\d{12}|\d{7})(?!\d)')
        d = defer.succeed('')
        is_billcode = re_express_billcodes.search(info['message'])
        debug('is_billcode: %s' % is_billcode)
        if is_billcode:
            billcodes = re_express_billcodes.findall(info['message'])

            d = getZTOTracking(billcodes)
            d.addCallback(self._make_text_reply, sender=info['sender'], 
                                            receiver=info['receiver'])
        else:
            # if not found any billcode transfer the message to service
            d = defer.succeed(info['message'])
            d.addCallback(self._make_transfer_reply, sender=info['sender'],
                                            receiver=info['receiver'])
        return d

    def _event_click(self, **kw):
        info = self._get_common_info(**kw)
        debug('received click event info: %s' % info)
        event_key = kw.get('event_key', '')
        debug('received event key: %s' % event_key)
        if not event_key: return ''
        if event_mapping.has_key(event_key):
            message = event_mapping.get(event_key, '')
            return self._make_text_reply(message, sender=info['sender'],
                                           receiver=info['receiver'])
        return ''

    def _event_subscribe(self, **kw):
        return ''

    def _invalid_event(self, **kw):
        event = kw.get('event', '')
        debug('Got an invalide event "%s").' % event)
        return ''

    def _invalid_msg_type(self, **kw):
        mtype = kw.get('mtype', '')
        debug('Got an invalide message type "%s".' % mtype)
        return ''

