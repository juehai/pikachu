# -*- coding: utf-8 -*-
import json
from wechat import WeChat
from datetime import datetime
from config import config
from search_engine import create_index


def generate_download_shell(access_token, media_list):
    dirname = '/home/www/notes4.com/apuniang/wechat_materials'
    command = """/home/tops/bin/parallel -N2 curl --data \'{1}\' -X POST 'https://api.weixin.qq.com/cgi-bin/material/get_material?access_token=%s' -o %s/{2}.jpg < media_id.list"""
    command = command % (access_token, dirname)

    with open('media_id.list', 'w+') as f:
        for mid in media_list:
            line = '%s\n%s\n' % (json.dumps(dict(media_id=mid)), mid)
            f.write(line)
        f.close()
    return command
    

def fill_pic_url(media_id):
    baseurl = 'http://notes4.com/apuniang/wechat_materials/%s.jpg'
    return baseurl % media_id
    

def build():
    _config = config.get('WeChat', None)
    _wechat = WeChat(_config)

    docs = list()
    ret = _wechat.getMaterialsList('news', get_all=True)
    media_list = list()
    for item in ret['item']:
        news_item = item['content']['news_item'][0]
        media_list.append(news_item['thumb_media_id'])
        doc = dict(
                thumb_media_id = news_item['thumb_media_id'],
                title = '%s' % (news_item['title']),
                url = news_item['url'],
                show_cover_pic = news_item['show_cover_pic'],
                cover_pic_url = fill_pic_url(news_item['thumb_media_id']),
                summary = '%s' % (news_item['digest']),
                content = '%s' % (news_item['content']),
                update_time = datetime.fromtimestamp(item['update_time']),
                content_source_url = news_item['content_source_url'],
                )
        docs.append(doc)

    create_index(docs, indexdir=_config['INDEX_DIR'])
    print "=" * 20
    print "Finished creating index."
    print generate_download_shell(_wechat.getAccessToken(), media_list)

if __name__ == '__main__':
    build()
