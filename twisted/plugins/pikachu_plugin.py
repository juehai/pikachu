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

        yaml = self.configure(c)
        from pikachu.service import site_configure
        site_root = site_configure(yaml)
        from twisted.web import server
        site = server.Site(site_root)

        from twisted.internet import reactor
        reactor.suggestThreadPoolSize(int(yaml.http.get("max_threads", 5)))

        return internet.TCPServer(int(options["port"] or 9000), site)


serviceMaker = PikachuServiceMaker()
