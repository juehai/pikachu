from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from collections import namedtuple
import codecs
import yaml


class Options(usage.Options):
    optParameters = [
        ["config", "c", "etc/default.yaml",
         "Path (or name) of sitebase configuration."],
        ["port", "p", 0, "The port number to listen on."],
        ["host", "i", 0, "The host ip to set up."],
    ]

YAMLConfiguration = namedtuple("YAMLConfiguration",
                               ['http', 'wechat', 'simsimi', 'celery'])


class PikachuServiceMaker(object):
    implements(IServiceMaker, IPlugin)

    tapname = "pikachu"
    description = "pikachu WeChat message gateway"
    options = Options

    def configure(self, c):
        with codecs.open(c, "r", encoding="utf-8") as f:
            http, wechat, simsimi, celery = yaml.load_all(f.read())

        return YAMLConfiguration(http=http,
                                 wechat=wechat,
                                 simsimi=simsimi,
                                 celery=celery)

    def makeService(self, options):
        c = options["config"]

        config = self.configure(c)
        from pikachu.service import site_configure
        site_root = site_configure(config)
        from twisted.web import server
        site = server.Site(site_root)

        # initial WeChat client
        from pikachu.backend.wechat import WeChatSDK
        WeChatSDK.setup(token=config.wechat.get('TOKEN', ''),
                     appid=config.wechat.get('APPID', ''),
                     appsecret=config.wechat.get('APPSECRET', ''),
                     expires_in=config.wechat.get('EXPIRES_IN)', 0)
        )

        # initial Redis connection pool
        from pikachu.backend.redis import PikachuRedis
        try:
            redis_host, redis_port = config.http.get("redis_host", '127.0.0.1:6379').split(":")
        except ValueError as e:
            redis_host, redis_port = config.http.get("redis_host", "127.0.0.1"), 6379
        PikachuRedis.setup(host=redis_host, port=int(redis_port), poolsize=5)

        # initial HTTP server
        from twisted.internet import reactor
        reactor.suggestThreadPoolSize(int(config.http.get("max_threads", 5)))
        try:
            host, port = config.http.get('bind', '127.0.0.1:9000').split(":")
        except ValueError as e:
            host, port = config.http.get('bind', '127.0.0.1'), 9000

        return internet.TCPServer(int(options["port"] or port), site,
                                  interface=(str(options["host"] or host)))


serviceMaker = PikachuServiceMaker()
