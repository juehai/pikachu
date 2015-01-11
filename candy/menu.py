#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import json
import requests

API = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=5r_2Pjpqjk-P1gtZX46Mpp3yw44IjidCsEcMW2LUNtePa3y-xfhD0N_NFo5SEgMEn--P2GbY45Cdj41YEQ7suRH8_hZTFZOxaodA-eTsCVQ'

def getConfig(cfile):
    config = dict()
    try:
        with open(cfile, 'rb') as f:
            config = yaml.load(f.read())
            f.close()
    except IOError as e:
        log.error(str(e))
        sys.exit(2)
    except KeyError as e:
        log.error('Include config(%s) does not exist.' % str(e))
        sys.exit(3)
    except Exception as e:
        raise
    return config
    

def main():
    try:
        resp = requests.post(API, data=menu, timeout=10)
        ret = resp.json()
        print ret
    except Exception as e:
        raise
        #app.logging.error('WeChat menu API request failed.')

if __name__ == '__main__':
    menu = getConfig('menu.yaml')
    menu = json.dumps(menu)
    print menu

    main()

