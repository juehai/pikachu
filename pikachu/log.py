# -*- coding: utf-8 -*-
# Author: Yang Gao<gaoyang.public@gmail.com>

from twisted.python.log import msg as _log
import logging

__all__ = ['debug', 'info', 'warn', 'error', 'crit']

def debug(msg, **args):
    return _log("DEBUG: %s" % msg, *args, level=logging.DEBUG)

def info(msg, **args):
    return _log(msg, *args, level=logging.INFO)

def warn(msg, **args):
    return _log(msg, *args, level=logging.WARNING)

def error(msg, **args):
    return _log(msg, *args, level=logging.ERROR)

def crit(msg, **args):
    return _log(msg, *args, level=logging.CRITICAL)
