# -*- coding: utf-8 -*-
import os
import yaml
import hashlib
import time
from datetime import datetime
from pikachu import httpclient
from pikachu import json_encode, json_decode

from twisted.internet import defer

try:
    from lxml import etree
except ImportError:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

class WeChatRuntimeError(Exception):
    pass

class WeChatValidateError(WeChatRuntimeError):
    pass

class WeChatSDK(object):
    baseapi = 'https://api.weixin.qq.com/cgi-bin'

    def __init__(self, token='', appid='',
                 appsecret='', expires_in=0):
        self.token = token
        self.appid = appid
        self.appsecret = appsecret
        self.expires_in = expires_in

    def validate(self, signature, timestamp, nonce):
        '''
        :param signature: A string signature parameter
        :param timestamp: A int timestamp parameter
        :param nonce: A int nonce parameter
        '''
        if not self.token:
            raise WeChatValidateError()
        if self.expires_in:
            try:
                timestamp = int(timestamp)
            except:
                # fake timestamp
                return False

            delta = time.time() - timestamp
            if delta <0:
                # this is a fake timestamp
                return False

            if delta > self.expires_in:
                # expired timestamp
                return False

        values = [self.token, str(timestamp), str(nonce)]
        s = ''.join(sorted(values))
        hsh = hashlib.sha1(s.encode('utf-8')).hexdigest()

        return signature == hsh

    @staticmethod
    def parse(self, content):
        def _format(args):
            timestamp = int(args.get('CreateTime', 0))
            _ = dict(
                id = args.get('MsgId', ''),
                timestamp=timestamp,
                receiver=args.get('ToUserName'),
                sender=args.get('FromUserName'),
                type=args.get('MsgType'),
                time=datetime.fromtimestamp(timestamp),
            )
            return _

        raw = {}
        root = etree.fromstring(content)
        for child in root:
            raw[child.tag] = child.text
        formatted = _format(raw)

        msg_type = formatted.get('type', 'invalid_type')
        msg_parser = getattr(self, '_parse_%s' % msg_type, None)
        if callable(msg_parser):
            parsed = msg_parser(raw)
        else:
            parsed = self.parse_invalid_type(raw)

        formatted.update(parsed)
        return formatted

    def _parse_text(self, raw):
        return {'content': raw.get('Content')}

    def _parse_image(self, raw):
        return {'picurl': raw.get('PicUrl')}

    def _parse_location(self, raw):
        return {
            'location_x': raw.get('Location_X'),
            'location_y': raw.get('Location_Y'),
            'scale': int(raw.get('Scale', 0)),
            'label': raw.get('Label'),
        }

    def _parse_link(self, raw):
        return {
            'title': raw.get('Title'),
            'description': raw.get('Description'),
            'url': raw.get('url'),
        }

    def _parse_event(self, raw):
        return {
            'event': raw.get('Event'),
            'event_key': raw.get('EventKey'),
            'ticket': raw.get('Ticket'),
            'latitude': raw.get('Latitude'),
            'longitude': raw.get('Longitude'),
            'precision': raw.get('Precision'),
        }

    def _parse_invalid_type(self, raw):
        return {}

    @defer.inlineCallbacks
    def getAccessToken(self):
        api = '%s/token' % self.baseapi
        params = dict(
            grant_type = 'client_credential',
            appid = self.appid,
            secret = self.appsecret,
        )
        #from twisted.web.client import getPage
        #from urllib import urlencode
        #api = '%s?%s' % (api, urlencode(params))

        page = yield httpclient(api, method=b'GET', params=params)
        ret = json_decode(page)
        timestamp = time.time()
        ret.update(dict(timestamp=timestamp))
        defer.returnValue(ret)

    def getUserInfo(self, openid, lang='zh_CN'):
        pass

    def getMaterialList(self, mtype, offset=0, count=20, get_all=False):
        pass

    def getMaterialCount(self):
        pass

    def getMaterial(self, media_id):
        pass

def display(val, *args, **kw):
    print str(val)
    reactor.stop()

if __name__ == '__main__':
    pass
