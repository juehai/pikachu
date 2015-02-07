# -*- coding: utf-8 -*-
import yaml
import time
import hashlib
import requests
from datetime import datetime
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

try:
    from lxml import etree
except ImportError:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree


__all__ = ('WeChat',)
__version__ = '0.4.0'
__author__ = ['Yang Gao <gaoyang.public@gmail.com>',
              'Hsiaoming Yang <me@lepture.com>']

class WeChat(object):
    sex_mapping = {1: u'帅锅',
                   2: u'菇凉',
                   0: u''}
    
    def __init__(self, config):
        self.token = config.get('TOKEN', None)
        self.baseapi = config.get('BASEAPI', '')
        self.appid = config.get('APPID', '')
        self.appsecret = config.get('APPSECRET', '')
        self.expires_in = config.get('EXPIRES_IN', 0)
        self._hooks = []
        self._hooks_mapping = {}
        
    def validate(self, signature, timestamp, nonce):
        """Validate request signature.
    
        :param signature: A string signature parameter sent by WeChat.
        :param timestamp: A int timestamp parameter sent by WeChat.
        :param nonce: A int nonce parameter sent by WeChat.
        """
        if not self.token:
            raise RuntimeError('TOKEN is missing')
    
        if self.expires_in:
            try:
                timestamp = int(timestamp)
            except:
                # fake timestamp
                return False
    
            delta = time.time() - timestamp
            if delta < 0:
                # this is a fake timestamp
                return False
    
            if delta > self.expires_in:
                # expired timestamp
                return False
    
        values = [self.token, str(timestamp), str(nonce)]
        s = ''.join(sorted(values))
        hsh = hashlib.sha1(s.encode('utf-8')).hexdigest()
        return signature == hsh

    def getAccessToken(self):
        # get access token from cache
        try:
            with open('.access_token', 'r') as f:
                _ret = yaml.load(f.read())
                delta = time.time() - timestamp
                if delta < 0:
                    # fake timestamp
                    raise
                elif delta > _ret['expires_in']:
                    raise

                f.close()
                return _ret['access_token']
        except:
            pass

        # refresh access token
        api = '%s/token' % self.baseapi
        params = {"grant_type": 'client_credential',
                  "appid"     : self.appid,
                  "secret"    : self.appsecret}

        try:
            resp = requests.get(api, params=params, timeout=10)
            ret = resp.json()
            timestamp = time.time()
            timeframe = {'timestamp': timestamp}
            ret.update(timeframe)
        except Exception as e:
            raise RuntimeError('WeChat api(getAccessToken) failed.')

        # cache access token
        try:
            with open('.access_token', 'w+') as f:
                f.write(yaml.dump(ret))
                f.close()
        except IOError as e:
            raise RuntimeError('Cannot open access_token file.')

        return ret['access_token']
                

    def getUserInfo(self, openid, lang='zh_CN'):
        api = '%s/user/info' % self.baseapi
        access_token = self.getAccessToken()
        params = {"access_token": access_token, 
                  "openid": openid,
                  "lang": lang}
        try:
            resp = requests.get(api, params=params, timeout=10)
            ret = resp.json()
            ret.update(dict(wrap_sex=self.sex_mapping[ret['sex']]))
        except Exception as e:
            raise RuntimeError('WeChat api(getUserInfo) failed.')

        return ret
        

    def parse(self, content):
        """Parse xml body sent by WeChat.

        :param content: A text of xml body.
        """
        raw = {}
        root = etree.fromstring(content)
        for child in root:
            raw[child.tag] = child.text

        formatted = self.format(raw)

        msg_type = formatted['type']
        msg_parser = getattr(self, 'parse_%s' % msg_type, None)
        if callable(msg_parser):
            parsed = msg_parser(raw)
        else:
            parsed = self.parse_invalid_type(raw)

        formatted.update(parsed)
        return formatted

    def format(self, kwargs):
        timestamp = int(kwargs.get('CreateTime', 0))
        return {
            'id': kwargs.get('MsgId'),
            'timestamp': timestamp,
            'receiver': kwargs.get('ToUserName'),
            'sender': kwargs.get('FromUserName'),
            'type': kwargs.get('MsgType'),
            'time': datetime.fromtimestamp(timestamp),
        }

    def parse_text(self, raw):
        return {'content': raw.get('Content')}

    def parse_image(self, raw):
        return {'picurl': raw.get('PicUrl')}

    def parse_location(self, raw):
        return {
            'location_x': raw.get('Location_X'),
            'location_y': raw.get('Location_Y'),
            'scale': int(raw.get('Scale', 0)),
            'label': raw.get('Label'),
        }

    def parse_link(self, raw):
        return {
            'title': raw.get('Title'),
            'description': raw.get('Description'),
            'url': raw.get('url'),
        }

    def parse_event(self, raw):
        return {
            'event': raw.get('Event'),
            'event_key': raw.get('EventKey'),
            'ticket': raw.get('Ticket'),
            'latitude': raw.get('Latitude'),
            'longitude': raw.get('Longitude'),
            'precision': raw.get('Precision'),
        }

    def parse_invalid_type(self, raw):
        return {}


    def render(self, username, type='text', sender=None, **kwargs):
        assert(False)

        """Create the reply text for WeChat.

        The reply varies per reply type. The acceptable types are `text`,
        `music` and `news`. Each type accepts different parameters, but
        they share some common parameters:

            * username: the receiver's username
            * type: the reply type, aka text, music and news
            * sender: sender is optional if you have a default value

        Text reply requires an additional parameter of `content`.

        Music reply requires 4 more parameters:

            * title: A string for music title
            * description: A string for music description
            * music_url: A link of the music
            * hq_music_url: A link of the high quality music

        News reply requires an additional parameter of `articles`, which
        is a list/tuple of articles, each one is a dict:

            * title: A string for article title
            * description: A string for article description
            * picurl: A link for article cover image
            * url: A link for article url
        """
        if not sender:
            sender = self.sender

        if not sender:
            raise RuntimeError('SENDER is missing')

        if type == 'text':
            content = kwargs.get('content', '')
            return text_reply(username, sender, content)

        if type == 'music':
            values = {}
            for k in ('title', 'description', 'music_url', 'hq_music_url'):
                values[k] = kwargs.get(k)
            return music_reply(username, sender, **values)

        if type == 'news':
            items = kwargs.get('articles', [])
            return news_reply(username, sender, *items)

        return None

    def register(self, key=None, func=None, **kwargs):
        """Register a command helper function.

        You can register the function::

            def print_help(**kwargs):
                username = kwargs.get('sender')
                sender = kwargs.get('receiver')
                return wechat.reply(
                    username, sender=sender, content='text reply'
                )

            wechat.register('help', print_help)

        It is also accessible as a decorator::

            @wechat.register('help')
            def print_help(*args, **kwargs):
                username = kwargs.get('sender')
                sender = kwargs.get('receiver')
                return wechat.reply(
                    username, sender=sender, content='text reply'
                )
        """
        if func:
            if key is None:
                limitation = frozenset(kwargs.items())
                self._hooks.append((func, limitation))
            else:
                self._hooks_mapping[key] = func
            return func

        return self.__call__(key, **kwargs)


    def __call__(self, key, **kwargs):
        """Register a reply function.

        Only available as a decorator::

            @weixin('help')
            def print_help(*args, **kwargs):
                username = kwargs.get('sender')
                sender = kwargs.get('receiver')
                return weixin.render(
                    username, sender=sender, content='text reply'
                )
        """
        def wrapper(func):
            self.register(key, func=func, **kwargs)
            return func

        return wrapper

#####   def music_reply(username, sender, **kwargs):
#####       kwargs['shared'] = _shared_reply(username, sender, 'music')
#####   
#####       template = (
#####           '<xml>'
#####           '%(shared)s'
#####           '<Music>'
#####           '<Title><![CDATA[%(title)s]]></Title>'
#####           '<Description><![CDATA[%(description)s]]></Description>'
#####           '<MusicUrl><![CDATA[%(music_url)s]]></MusicUrl>'
#####           '<HQMusicUrl><![CDATA[%(hq_music_url)s]]></HQMusicUrl>'
#####           '</Music>'
#####           '</xml>'
#####       )
#####       return template % kwargs
#####   
#####   
#####   def news_reply(username, sender, *items):
#####       item_template = (
#####           '<item>'
#####           '<Title><![CDATA[%(title)s]]></Title>'
#####           '<Description><![CDATA[%(description)s]]></Description>'
#####           '<PicUrl><![CDATA[%(picurl)s]]></PicUrl>'
#####           '<Url><![CDATA[%(url)s]]></Url>'
#####           '</item>'
#####       )
#####       articles = map(lambda o: item_template % o, items)
#####   
#####       template = (
#####           '<xml>'
#####           '%(shared)s'
#####           '<ArticleCount>%(count)d</ArticleCount>'
#####           '<Articles>%(articles)s</Articles>'
#####           '</xml>'
#####       )
#####       dct = {
#####           'shared': _shared_reply(username, sender, 'news'),
#####           'count': len(items),
#####           'articles': ''.join(articles)
#####       }
#####       return template % dct
#####   
#####   
#####   def _shared_reply(username, sender, type):
#####       dct = {
#####           'username': username,
#####           'sender': sender,
#####           'type': type,
#####           'timestamp': int(time.time()),
#####       }
#####       template = (
#####           '<ToUserName><![CDATA[%(username)s]]></ToUserName>'
#####           '<FromUserName><![CDATA[%(sender)s]]></FromUserName>'
#####           '<CreateTime>%(timestamp)d</CreateTime>'
#####           '<MsgType><![CDATA[%(type)s]]></MsgType>'
#####       )
#####       return template % dct

class WeChatReply(object):

    def __init__(self, sender=None, receiver=None, type=None, **kw):
        self.sender = sender
        self.receiver = receiver
        self.type = type

        for k, v in kw.items():
            setattr(self, k, v)
    
    def _shared_reply(self, type):
        dct = {
            'username': self.receiver,
            'sender': self.sender,
            'type': self.type,
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
