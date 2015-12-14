# -*- coding: utf-8 -*-
import os
import yaml
import hashlib
import time
from datetime import datetime
from pikachu import httpclient
from pikachu import json_encode, json_decode
from pikachu.backend.redis import dStore
from pikachu.log import *

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

class WeChatInvalidCache(WeChatRuntimeError):
    pass

class WeChatSDK(object):
    baseapi = 'https://api.weixin.qq.com/cgi-bin'

    @classmethod
    def setup(cls, token='', appid='',
              appsecret='', expires_in=0):
        WeChatSDK.token = token
        WeChatSDK.appid = appid
        WeChatSDK.appsecret = appsecret
        WeChatSDK.expires_in = expires_in

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

    def parse(self, content):
        def _format(args):
            timestamp = int(args.get('CreateTime', 0))
            _ = dict(
                mid = args.get('MsgId', ''),
                timestamp=timestamp,
                receiver=args.get('ToUserName'),
                sender=args.get('FromUserName'),
                mtype=args.get('MsgType'),
                time=datetime.fromtimestamp(timestamp),
            )
            return _

        raw = {}
        root = etree.fromstring(content)
        for child in root:
            raw[child.tag] = child.text
        formatted = _format(raw)

        msg_type = formatted.get('mtype', 'invalid_type')
        msg_parser = getattr(self, '_parse_%s' % msg_type, None)
        if callable(msg_parser):
            parsed = msg_parser(raw)
        else:
            parsed = self._parse_invalid_type(raw)

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
    def _getAccessToken(self):
        # request access token
        api = '%s/token' % self.baseapi
        params = dict(
            grant_type = 'client_credential',
            appid = self.appid,
            secret = self.appsecret,
        )

        page = yield httpclient(api, method=b'GET', params=params)
        ret = json_decode(page)
        timestamp = time.time()
        ret.update(dict(timestamp=timestamp))

        defer.returnValue(ret)


    @defer.inlineCallbacks
    def getAccessToken(self):
        # get from cache
        try:
            _cache = yield dStore.hmget_cache('access_token')
            delta = time.time() - _cache.get('timestamp', 0)
            expires_in = int(_cache.get('expires_in', 7200))
            if delta < 0:
                #fake timestamp
                raise WeChatInvalidCache('Fake timestamp.')
            elif delta > expires_in:
                raise WeChatInvalidCache('Cache expires in %s senconds.' % expires_in)
            debug('got Access Token from cache.')
            defer.returnValue(_cache)
        except WeChatInvalidCache as e:
            debug('got Access Token from cache failed.')
            pass
        except Exception as e:
            error(str(e))
            raise e

        # refrush cache
        raw = yield self._getAccessToken() # request access token
        ret = yield dStore.hmset_cache('access_token', raw)
        defer.returnValue(raw)

    def getUserInfo(self, openid, lang='zh_CN'):
        pass

    def getMaterialList(self, mtype, offset=0, count=20, get_all=False):
        pass

    def getMaterialCount(self):
        pass

    def getMaterial(self, media_id):
        pass


class WeChatReply(object):

    def __init__(self, sender=None, receiver=None, mtype=None, **kw):
        self.sender = sender
        self.receiver = receiver
        self.mtype = mtype

        for k, v in kw.items():
            setattr(self, k, v)

    def _shared_reply(self, mtype):
        dct = {
            'username': self.receiver,
            'sender': self.sender,
            'type': mtype,
            'timestamp': int(time.time()),
        }
        template = (
            '<ToUserName><![CDATA[%(username)s]]></ToUserName>'
            '<FromUserName><![CDATA[%(sender)s]]></FromUserName>'
            '<CreateTime>%(timestamp)d</CreateTime>'
            '<MsgType><![CDATA[%(type)s]]></MsgType>'
        )
        return template % dct

    def _make_article(self, item):
        template = (
            '<item>'
            '<Title><![CDATA[%(title)s]]></Title>'
            '<Description><![CDATA[%(desc)s]]></Description>'
            '<PicUrl><![CDATA[%(picurl)s]]></PicUrl>'
            '<Url><![CDATA[%(url)s]]></Url>'
            '</item>'
        )
        return template % item

    def transfer_customer_service(self):
        shared = self._shared_reply('transfer_customer_service')
        template = '<xml>%s</xml>'
        return template % shared

    def text_reply(self):
        shared = self._shared_reply('text')
        template = '<xml>%s<Content><![CDATA[%s]]></Content></xml>'
        return template % (shared, self.content)

    def image_reply(self):
        shared = self._shared_reply('image')
        template = '<xml>%s<Image><MediaId>%s</MediaId></Image></xml>'
        return template % (shared, self.media_id)

    def news_reply(self):
        shared = self._shared_reply('news')
        template = '<xml>%s<ArticleCount>%s</ArticleCount><Articles>%s</Articles></xml>'
        article_content = map(lambda item: self._make_article(item), self.articles)
        return template % (shared, len(article_content), '\n'.join(article_content))


if __name__ == '__main__':
    pass
