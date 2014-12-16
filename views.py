# -*- coding: utf-8 -*-
from config import config
from flask import request, Response
from wechat import WeChat
from hooks import *

__all__ = ['hello', 'wechat']

_config = config.get('WeChat', None)
_wechat = WeChat(_config)
_wechat.register('*', simsimi_reply)
_wechat.register('normal', normal_reply)

def hello():
    return "Hello, I'm Pikachu."

def wechat():
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    if not _wechat.validate(signature, timestamp, nonce):
        return 'signature failed', 400

    if request.method == 'GET':
        echostr = request.args.get('echostr')
        return echostr

    try:
        ret = _wechat.parse(request.data)
    except:
        return 'invalid', 400

    if 'type' not in ret:
        # not a valid message
        return 'invalid', 400

    if ret['type'] == 'text' and ret['content'] in _wechat._hooks:
        func = _wechat._hooks[ret['content']]
    else:
        ret_set = frozenset(ret.items())
        matched_rules = (
            _func for _func, _limitation in _wechat._hooks_mapping
            if _limitation.issubset(ret_set))
        func = next(matched_rules, None)  # first matched rule

    if func is None:
        if '*' in _wechat._hooks:
            func = _wechat._hooks['*']
        else:
            func = 'failed'

    if callable(func):
        text = func(**ret)
    else:
        # plain text
        text = _wechat.reply(
            username=ret['sender'],
            sender=ret['receiver'],
            content=func,
        )

    return Response(text, content_type='text/xml; charset=utf-8')
