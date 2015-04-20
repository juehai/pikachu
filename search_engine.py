#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authour: Yang Gao<gaoyang.public@gmail.com>
from __future__ import unicode_literals
import sys,os
sys.path.append("../")

import os, os.path
import jieba
from whoosh import index
from whoosh import writing
from whoosh import sorting
from whoosh.fields import *
from whoosh.filedb.filestore import FileStorage
from whoosh.qparser import QueryParser, MultifieldParser
from jieba.analyse import ChineseAnalyzer

def get_schema():
    analyzer = ChineseAnalyzer()
    schema = Schema(thumb_media_id=ID(stored=True), 
                    title=TEXT(stored=True, field_boost=2.0, analyzer=analyzer), 
                    url=STORED, 
                    content_source_url=STORED,
                    show_cover_pic=STORED,
                    cover_pic_url=STORED,
                    summary=TEXT(stored=True, analyzer=analyzer), 
                    content = TEXT(stored=True, analyzer=analyzer),
                    update_time=DATETIME)
    return schema

def get_myindex(indexdir='indexdir', filestore=False):
    schema = get_schema()
    if not filestore:
        if not os.path.exists(indexdir):
            os.mkdir(indexdir)
            ix = index.create_in(indexdir, schema)
        ix = index.open_dir(indexdir)
    else:
        storage = FileStorage(indexdir)
        # TODO: When the indexdir has already exist
        #       the index object also use create_index,
        #       it should use open_dir as above method.
        ix = storage.create_index(schema)
    return ix

def create_index(docs, indexdir='indexdir'):
    ix = get_myindex(indexdir=indexdir)
    with ix.writer() as writer:
        for doc in docs:
            writer.add_document(**doc)
        writer.mergetype = writing.CLEAR

def split_keywords(qstring):
    keywords = jieba.cut_for_search(qstring)
    keywords = [ kw.strip() for kw in keywords if kw.strip() != '' ]
    return keywords
    

def search(ix, query_string, sortedby=None, limit=10):
    mp = MultifieldParser(["title", "summary"], schema=ix.schema)
    
    s = ix.searcher()
    keywords = split_keywords(query_string)
    user_q = mp.parse(' OR '.join(keywords))
    # TODO: add query filter
    results = s.search(user_q, sortedby=sortedby, limit=limit)
    return results
    
if __name__ == '__main__':
    from wechat import WeChat
    from datetime import datetime
    from config import config

    # TODO: NEED to make arguments for commandline.
    #       1. search from query string
    #       2. input indexdir and create index
    #       3. extra options e.g. sortedby, limit...

    _config = config.get('WeChat', None)

    ##_wechat = WeChat(_config)

    ##docs = list()
    ##ret = _wechat.getMaterialsList('news', get_all=True)
    ##for item in ret['item']:
    ##    news_item = item['content']['news_item'][0]
    ##    doc = dict(
    ##            thumb_media_id = news_item['thumb_media_id'],
    ##            title = '%s' % (news_item['title']),
    ##            url = news_item['url'],
    ##            show_cover_pic = news_item['show_cover_pic'],
    ##            summary = '%s' % (news_item['digest']),
    ##            content = '%s' % (news_item['content']),
    ##            update_time = datetime.fromtimestamp(item['update_time']),
    ##            content_source_url = news_item['content_source_url'],
    ##            )
    ##    docs.append(doc)

    ##create_index(docs, indexdir=_config['INDEX_DIR'])

    ix = get_myindex(indexdir=_config['INDEX_DIR'])
    date_facet = sorting.FieldFacet("update_time", reverse=True)
    scores = sorting.ScoreFacet()
    results = search(ix, '奶粉', sortedby=[date_facet, scores])
    print bool(results)
    for hit in results:
        print hit['title']
    print "=" * 10
