# -*- coding: utf-8 -*-
import time
import requests
from config import config
from wechat import WeChat, WeChatReply
from flask import current_app as app

_config = config.get('WeChat', None)
_wechat = WeChat(_config)

__all__ = ['simsimi_reply', 'normal_reply', 'event_reply']

def simsimi_reply(**kw):
    _conf    = config.get('SIMSIMI', None)
    base_api = _conf.get('API', None)
    timeout  = _conf.get('TIMEOUT', None)
    key = _conf.get('KEY', None)

    sender = kw.get('receiver', '')
    receiver = kw.get('sender', '')
    content = kw.get('content', '')
    type = kw.get('type', '')

    params = dict( key   = key,
                  lc    = 'ch',
                  text  = content,
                  ft    = '1.0',
                )

    try:
        resp = requests.get(base_api, params=params, timeout=10)
        ret = resp.json()
    except Exception as e:
        app.logging.error('SimSimi API request failed.')

    if 'response' in ret:
        content = ret['response']

    reply = WeChatReply(sender=sender, 
                        receiver=receiver,
                        type=type,
                        content=content)
    msg = reply.text_reply()
    return msg
    
def normal_reply(**kw):
    sender = kw.get('receiver', '')
    receiver = kw.get('sender', '')
    content = kw.get('content', '')
    type = kw.get('type', '')

    reply = WeChatReply(sender=sender, 
                        receiver=receiver,
                        type=type,
                        content=content)
    msg = reply.text_reply()
    return msg

def event_reply(**kw):
    sender = kw.get('receiver', '')
    receiver = kw.get('sender', '')
    event = kw.get('event', '')
    type = kw.get('type', '')

    msg = ''
    
    if event == u'subscribe':
        user = _wechat.getUserInfo(receiver)
        content = u'你好 %s %s，感谢您关注阿扑娘滴新西兰纯净小店，请您持续关注这个公众号，也许你会发现惊喜。' % (user['nickname'], 
                                                                                                                 user['wrap_sex'])
        reply = WeChatReply(sender=sender, 
                            receiver=receiver,
                            type='text',
                            content=content)
        msg = reply.text_reply()
    
    return msg
