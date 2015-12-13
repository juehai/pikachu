# -*- coding: utf-8 -*-
# Author: Yang Gao<gaoyang.public@gmail.com>
from twisted.internet import reactor
from twisted.internet import defer
from txredisapi import lazyConnectionPool, ConnectionPool
#from pikachu.log import *

__all__ = ['dStore', 'PikachuRedis']

class PikachuRedis(object):
    client = None

    @classmethod
    def setup(cls, host, port=6379, poolsize=5):
        PikachuRedis.client = lazyConnectionPool(host=host, port=port,
                                     poolsize=poolsize, reconnect=False)
        return cls.client

    @defer.inlineCallbacks
    def hmset_cache(self, key, value):
        key = 'cache:%s' % key
        print '*'*80, self.client
        res = yield self.client.hmset(key, value)
        defer.returnValue(res)

    @defer.inlineCallbacks
    def hmget_cache(self, key):
        key = 'cache:%s' % key
        ret = yield self.client.hgetall(key)
        defer.returnValue(ret)

    @defer.inlineCallbacks
    def info(self):
        info = yield self.client.info()
        defer.returnValue(info)

dStore = PikachuRedis()

if __name__ == '__main__':
    dStore.setup('127.0.0.1')
    dStore.info()
    reactor.run()
