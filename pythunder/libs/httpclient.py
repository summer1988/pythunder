#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: httpclient.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-06 23:19
#

import requests

try:
    from UserDict import DictMixin
except ImportError:
    from collections import Mapping as DictMixin

from pythunder import PyThunderBase

__all__ = ('HttpClientBase', 'DefaultHttpClient')


class Response(requests.Response):
    """

    """
    def __init__(self):
        pass

    def __setitem__(self, key, value):
        pass

    def __getitem__(self, item):
        pass


class HttpClientBase(PyThunderBase):
    """

    """
    def get(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request(method='GET', url=url, **kwargs)

    def head(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request(method='HEAD', url=url, **kwargs)

    def post(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request(method='POST', url=url, **kwargs)

    def delete(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request(method='DELETE', url=url, **kwargs)

    def request(self, *args, **kwargs):
        raise NotImplementedError

    def switchProxy(self, proxy):
        raise NotImplementedError

    def loadCookies(self, cookies):
        raise NotImplementedError


class DefaultHttpClient(requests.Session, HttpClientBase):
    """

    """
    def __init__(self):
        super(DefaultHttpClient, self).__init__()
        self.trust_env = False

    def switchProxy(self, proxy):
        self.proxies = proxy

    def loadCookies(self, cookies):
        self.cookies = cookies


if __name__ == '__main__':
    httpClient = DefaultHttpClient()
    resp = httpClient.get('http://www.qq.com', timeout=1)
    print('fetched: code: {} resp: {}'.format(resp.status_code, len(resp.content)))