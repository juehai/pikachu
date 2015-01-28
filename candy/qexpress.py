# -*- coding: utf-8 -*-
import requests
import re
from lxml import html

class QExpress(object):

    API = 'http://www.qexpress.co.nz/tracking.aspx?orderNumber=%s'

    def __init__(self):
        pass

    def _parser(self, content):
        '''
        ::return:: dict(
                        nz = {
                                "trackid": "zy030536033nz",
                                "tracking": [(t1, msg1), (t2, msg2), ...]
                             }
                        cn = {
                                "trackid": "BE032025975CN",
                                "tracking": [(t1, msg1), (t2, msg2), ...]
                             }
                            
        '''
        dataset = dict( nz = {}, cn = {})
        slice_table = re.compile(r'.*\<!--news specials videos-->(.*)<!--\/news specials videos-->', re.S)
        table = slice_table.findall(content)[0]
        table = re.sub(r'\/n', '', table)
        table = re.sub(r'\s\s+', '', table)

        tree = html.fromstring(table)
        nz_info = tree.xpath('table[1]//td[last()]/text()')
        print 'nz_info:'
        for line in nz_info:
            print line.encode('utf-8')

        nz_tracking = tree.xpath('table[2]/tr[position()>1]//td/text()')
        nz_tracking = zip(nz_tracking[0::2], nz_tracking[1::2])
        print 'nz_tracking:'
        for t, m in nz_tracking:
            print t.encode('utf-8'), m.encode('utf-8')

        cn_info = tree.xpath('table[3]//td/text()')
        print 'cn_info:'
        for line in cn_info:
            print line.encode('utf-8')

        cn_tracking = tree.xpath('table[4]/tr[position()>1]//td/text()')
        cn_tracking = zip(cn_tracking[0::2], cn_tracking[1::2])
        print 'cn_tracking:'
        for t, m in cn_tracking:
            print t.encode('utf-8'), m.encode('utf-8')

        return dataset

    def fetch(self, express_id):
        url = self.API % express_id
        content = requests.get(url).text
        print self._parser(content)

if __name__ == '__main__':
    obj = QExpress()
    obj.fetch('zy030536093nz')
        
