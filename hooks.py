# -*- coding: utf-8 -*-
import time
import requests
from config import config
from wechat import WeChat, WeChatReply
from flask import current_app as app

_config = config.get('WeChat', None)
_wechat = WeChat(_config)

__all__ = ['no_reply', 'simsimi_reply', 'normal_reply', 'event_reply']

def no_reply(**kw):
    return ''
    

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
        content = u'客服小黄鸡: %s' % ret['response']

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
        content = u'你好 %s<%s> 感谢您关注阿扑娘滴新西兰纯净小店，真心希望您持续关注这个公众号，也许您会发现更多惊喜 :)' % (user['wrap_sex'],user['nickname'])
        reply = WeChatReply(sender=sender, 
                            receiver=receiver,
                            type='text',
                            content=content)
        msg = reply.text_reply()

    if event == u'click':
        event_key = kw.get('eventkey', '')
        if event_key == 'V1001_APUNIANG_CARD':
            reply = WeChatReply(sender=sender,
                                receiver=receiver,
                                type='image',
                                media_id='2NfvX9lC0H4HSUjjw3Zj_1H3-HWQrgSF3j3a4ZREH5KAJZg9gteUoOifVC4VI2Yi')
            msg = reply.image_reply()
        elif event_key == 'V1002_PRODUCT_PRICE':
            #user = _wechat.getUserInfo(receiver)
            content = u'请直接联系美丽的 阿扑娘 了解产品详情，哈。点击菜单”找阿扑娘“获取 阿扑娘 的二维码 ：）'
            reply = WeChatReply(sender=sender,
                            receiver=receiver,
                            type='text',
                            content=content)
            msg = reply.text_reply()
        elif event_key == 'V1003_BORED':
            content = u'你确实挺无聊的，可是阿扑娘很忙，没空陪你聊天，哈。你还是跟客服小黄鸡逗逗乐子吧，哈。直接回复文字给这个公众号即可。'
            reply = WeChatReply(sender=sender,
                            receiver=receiver,
                            type='text',
                            content=content)
            msg = reply.text_reply()
    return msg
