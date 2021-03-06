# -*- coding: utf-8 -*-
import yaml
import os

__all__ = ['config', ]

def getConfig(cfile):
    config = dict()
    try:
        with open(cfile, 'rb') as f:
            sections = ['HTTP', 'WeChat', 'SIMSIMI']
            c = yaml.load_all(f.read())
            config = dict(zip(sections, c))
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

current_dir = os.path.dirname(os.path.realpath(__file__))
config_file = current_dir + '/prod.yaml'
config = getConfig(config_file)
