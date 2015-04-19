# -*- coding: utf-8 -*-
from config import config
from wechat import WeChat


_config = config.get('WeChat', None)
if __name__ == '__main__':

    _wechat = WeChat(_config)
    ret = _wechat.getMaterialsList('news', offset=50, count=2, get_all=False)
    for item in ret['item']:
        print item['content']['news_item'][0]['title'].encode('utf-8').decode('gbk')
