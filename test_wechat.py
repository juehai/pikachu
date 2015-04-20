# -*- coding: utf-8 -*-
from config import config
from wechat import WeChat


_config = config.get('WeChat', None)
if __name__ == '__main__':

    _wechat = WeChat(_config)
    ret = _wechat.getMaterialsList('news', get_all=True)
    print len(ret['item'])
    ret = _wechat.getMaterialCount()
    print ret
