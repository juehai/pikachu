# -*- coding: utf-8 -*-
# Author: Yang Gao<gaoyang.public@gmail.com>

from ujson import encode as json_encode, decode as json_decode

from twisted.web.client import getPage
from urllib import urlencode
from urllib3.util import parse_url
from urllib3.util.url import Url
from urllib3.exceptions import LocationParseError


class InvalidURL(Exception):
    pass

def _encode_params(data):
    if isinstance(data, (str, bytes)):
        return data
    elif hasattr(data, 'read'):
        return data
    elif hasattr(data, '__iter__'):
        result = []
        for k, vs in data.items():
            if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                vs = [vs]
            for v in vs:
                if v is not None:
                    result.append(
                        (k.encode('utf-8') if isinstance(k, str) else k,
                         v.encode('utf-8') if isinstance(v, str) else v))
        return urlencode(result, doseq=True)
    else:
        return data


def httpclient(url, **kw):
    if not 'method' in kw:
        kw['method'] = b'GET'
    if not 'agent' in kw:
        kw['agent'] = b'Pikachu Message Gateway HttpClient v0.1'
    if not 'timeout' in kw:
        kw['timeout'] = 10
    if not 'followRedirect' in kw:
        kw['followRedirect'] = True
    if not 'redirectLimit' in kw:
        kw['redirectLimit'] = 5

    if kw['method'] == b'GET':
        # Support for unicode domain names and paths.
        try:
            scheme, auth, host, port, path, query, fragment = parse_url(url)
        except LocationParseError as e:
            raise InvalidURL(*e.args)
        params = kw['params']
        del kw['params']

        enc_params = _encode_params(params)
        if enc_params:
            if query:
                query = '%s&%s' % (query, enc_params)
            else:
                query = enc_params

        url = Url(scheme, auth, host, port, path, query, fragment).url
    d = getPage(url, **kw)
    return d
