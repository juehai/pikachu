# -*- coding: utf-8 -*-
from config import config
from wechat import WeChat


_config = config.get('WeChat', None)
if __name__ == '__main__':

    _wechat = WeChat(_config)
    ret = _wechat.getMaterialsList('news', get_all=True)
    media_id = ret['item'][20]['content']['news_item'][0]['thumb_media_id']
    ret = _wechat.getMaterial(media_id)
    with open('a.jpg', 'w+') as f:
        f.write(str(ret))
        f.close()

