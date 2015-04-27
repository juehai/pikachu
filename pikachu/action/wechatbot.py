# -*- coding: utf-8 -*-
# Author: Yang Gao<gaoyang.public@gmail.com>
from pikachu.backend.wechat import WeChatSDK, WeChatReply
from pikachu.log import *

class WeChatBotRuntimeError(Exception):
    pass

class InvalidMsgType(WeChatBotRuntimeError):
    pass

class InvalidEventType(WeChatBotRuntimeError):
    pass

class WeChatBot(object):
    msg_type = ['text', 'image', 'news', 'event']
    event_type = ['click', 'subscribe' ]

    def __init__(self):
        pass

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

    def answer_text(self, **kw):
        info = self._get_common_info(**kw)
        if info['message'].startswith('trademe#'):
            info['content'] = u'Trademe Monitor has stoped.'
        else:
            info['content'] = info['message']

        reply = WeChatReply(
            sender=info['sender'],
            receiver=info['receiver'],
            mtype='text',
            content=info['content']
        )
        return reply.text_reply()

    def _event_click(self, **kw):
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
