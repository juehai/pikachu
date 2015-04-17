# -*- coding: utf-8 -*-
from config import config
from flask import request
from flask import Response
from flask import current_app as app
from wechat import WeChat
from hooks import *

__all__ = ['hello', 'wechat']

_config = config.get('WeChat', None)
_wechat = WeChat(_config)
#_wechat.register('*', no_reply)
#_wechat.register('normal', normal_reply)
_wechat.register('*', simsimi_reply)
_wechat.register('event', event_reply)
_wechat.register('trademe', system_control)

def hello():
    return "Hello, I'm Pikachu."

def wechat():
    res = request.data
    app.logger.debug('Response: %s' % res)

    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    if not _wechat.validate(signature, timestamp, nonce):
        app.logger.error('Error: signature faild.')
        return 'signature failed', 400

    if request.method == 'GET':
        echostr = request.args.get('echostr')
        return echostr

    try:
        ret = _wechat.parse(res)
        app.logger.debug("fmt_ret: %s" % ret)
    except:
        app.logger.error('Error: parse WeChat response fail.')
        return 'invalid', 400

    if 'type' not in ret:
        # not a valid message
        app.logger.error('Error: invalid WeChat response format data.')
        return 'invalid', 400

    if ret['type'] == 'event' and 'event' in _wechat._hooks_mapping:
        func = _wechat._hooks_mapping['event'] 
    if ret['content'].startswith('trademe#') and 'trademe' in _wechat.hooks_mapping:
        func = _wechat._hooks_mapping['trademe']
    else:
        if '*' in _wechat._hooks_mapping:
            func = _wechat._hooks_mapping['*']
        else:
            func = 'failed'

    if callable(func):
        text = func(**ret)
    else:
        app.logger.debug('func: %s' % func)
        return 'invalid', 500

    return Response(text, content_type='text/xml; charset=utf-8')
            
        

##    if ret['type'] == 'text' and ret['content'] in _wechat._hooks_mapping:
##        func = _wechat._hooks_mapping[ret['content']]
##    else:
##        ret_set = frozenset(ret.items())
##        matched_rules = (
##            _func for _func, _limitation in _wechat._hooks
##            if _limitation.issubset(ret_set))
##        func = next(matched_rules, None)  # first matched rule
##
##    if func is None:
##        if '*' in _wechat._hooks_mapping:
##            func = _wechat._hooks_mapping['*']
##        else:
##            func = 'failed'
##
##    if callable(func):
##        text = func(**ret)
##    else:
##        # plain text
##        text = _wechat.reply(
##            username=ret['sender'],
##            sender=ret['receiver'],
##            content=func,
##        )

##    return Response(text, content_type='text/xml; charset=utf-8')
