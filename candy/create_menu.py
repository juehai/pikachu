#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
from ujson import decode as json_decode, encode as json_encode
import requests
import sys

token = '195ZWfkVYnbDT-rxPhMMvZ8DrXmTsN2xzwFEQGzXkV5teP6o1IThHgZ2karVVPspQYJaLLaKKTen1_RNhY8zhXT_1K1rt4wkz8ni2PuW3XwPSVjAIAGJM'
API = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % token

def getConfig(cfile):
    config = dict()
    try:
        with open(cfile, 'rb') as f:
            content = f.read()
#            print content
#            config = json_decode(content)
#            print config
            config = content
            f.close()
    except IOError as e:
        sys.exit(2)
    except KeyError as e:
        sys.exit(3)
    except Exception as e:
        raise
    return config
    

def main(menu):
    try:
        resp = requests.post(API, data=menu, timeout=10)
        ret = resp.json()
        print ret
    except Exception as e:
        raise
        #app.logging.error('WeChat menu API request failed.')

if __name__ == '__main__':
    menu = getConfig('self_menu.json')
    print menu
    if not menu: raise

    main(menu)


