# -*- coding: utf-8 -*-
import time
import requests
import os
from config import config
from wechat import WeChat, WeChatReply
from flask import current_app as app

_config = config.get('WeChat', None)
_wechat = WeChat(_config)

__all__ = ['no_reply', 'simsimi_reply', 'normal_reply', 'event_reply', 'system_control']

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
        content = u'%s \n(扑小贱的瞎叨叨... :P)' % ret['response']

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
    event = kw.get('event', '').lower()
    type = kw.get('type', '')

    msg = ''
    
    if event == u'subscribe':
        user = _wechat.getUserInfo(receiver)
        content = u'你好 %s<%s> 感谢您关注阿扑娘滴新西兰纯净小店，真心希望您持续关注这个公众号，也许您会发现更多惊喜哟 :)' % (user['wrap_sex'],user['nickname'])
        reply = WeChatReply(sender=sender, 
                            receiver=receiver,
                            type='text',
                            content=content)
        msg = reply.text_reply()

    if event == u'click':
        event_key = kw.get('event_key', '')
        if event_key == 'V1001_APUNIANG_CARD':
            reply = WeChatReply(sender=sender,
                                receiver=receiver,
                                type='news',
                                articles = [dict(
                                    title=u'【阿扑娘温馨提示】如何联系到美丽的阿扑娘',
                                    desc=u'感谢亲们选择阿扑娘滴纯净小店，为了方便亲们更快的联系到阿扑娘，特此整理一个“如何快速联系到阿扑娘”的帖子～',
                                    picurl='https://mmbiz.qlogo.cn/mmbiz/TOc9B287AvovPxmDU2NI148RjSQtmItpI4UGYgOAFM2UwhbWyUbx6Cquh6m8jibSew6ekibwStZwGhTj3PEJiak6g/0',
                                    url='http://mp.weixin.qq.com/s?__biz=MzAxNzEzNDI1MQ==&mid=202754535&idx=1&sn=1c4eac7521c0ae226c364a0f2f39a40f#rd'),
                                    ]
                    )
            msg = reply.news_reply()
        elif event_key == 'V1002_PRODUCT_PRICE':
            #user = _wechat.getUserInfo(receiver)
            content = u'请直接联系阿扑娘的微信号，点击菜单“找阿扑娘”可以获取到阿扑娘的二维码'
            reply = WeChatReply(sender=sender,
                            receiver=receiver,
                            type='text',
                            content=content)
            msg = reply.text_reply()
        elif event_key == 'V1003_BORED':
            content = u'你确实挺无聊的，可是阿扑娘很忙，没空陪你聊天，哈。你还是跟小贱客服逗逗乐子吧，哈。直接回复文字给这个公众号即可。'
            reply = WeChatReply(sender=sender,
                            receiver=receiver,
                            type='text',
                            content=content)
            msg = reply.text_reply()
    return msg

def system_control(**kw):
    sender = kw.get('receiver', '')
    receiver = kw.get('sender', '')
    content = kw.get('content', '')
    type = kw.get('type', '')

    reply_content = 'Error: Unknown command.'

    program, command = content.split('#')
    if program == u'trademe':
        try:
            if command.lower() == 'stop':
                os.system('/usr/local/bin/svc -d /service/trademe')
                reply_content = 'Trademe Monitor has stoped.'
            elif command.lower() == 'start':
                os.system('/usr/local/bin/svc -u /service/trademe')
                reply_content = 'Trademe Monitor has started.'
        except Exception as e:
            reply_content = 'Error: %s' % e
    
    reply = WeChatReply(sender=sender, 
                        receiver=receiver,
                        type=type,
                        content=reply_content)
    msg = reply.text_reply()
    return msg
