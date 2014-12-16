# -*- coding: utf-8 -*-
import yaml

__all__ = ['config', ]

def getConfig(cfile):
    config = dict()
    try:
        with open(cfile, 'rb') as f:
            httpconf, wechat, simsimi = yaml.load_all(f.read())
            config['HTTP'] = httpconf
            config['WeChat'] = wechat
            config['SIMSIMI'] = simsimi
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

config = getConfig('prod.yaml')

