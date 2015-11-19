#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: qredis.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-10 11:25
#

import json

import redis

from six.moves.urllib_parse import urlparse, parse_qsl, urlencode

from pythunder.queues.qmsgs import MQBase


class RedisMQ(MQBase):
    """

    """
    max_timeout = 0.3

    def __init__(self, url):
        super(RedisMQ, self).__init__(url=url)
        url = self.fromUrl(url)
        self.redis = redis.StrictRedis.from_url(url)

    def qsize(self):
        self.lastQsize = self.redis.llen(self.name)
        return self.lastQsize

    def _put(self, item):
        return self.redis.rpush(self.name, item)

    def _get(self):
        return self.redis.lpop(self.name)

    def fromUrl(self, url):
        urlInfo = urlparse(url)
        options = dict(parse_qsl(urlInfo.query))
        self.name = options.pop('name', 'test')
        ignoreSuffix = options.pop('ignoreSuffix', False)
        self.suffix = options.pop('suffix', 'URL')
        try:
            ignoreSuffix = json.loads(ignoreSuffix)
        except:
            pass
        if not ignoreSuffix:
            self.name = self.name + ':' + self.suffix
        self.maxSize = options.pop('maxSize', 10000)
        self.lazyLimit = options.pop('lazyLimit', True)
        print('--options->: {} {} {} {}'.format(self.name, self.suffix, urlInfo, ignoreSuffix))
        qs = urlencode(options)
        url = url.split('?')[0] + qs
        return url

    def __repr__(self):
        return '{}@0x{}<queueName:{}>'.format(self.__class__, id(self), self.name)


if __name__ == '__main__':

    from pythunder import Task

    t = Task()
    rq = RedisMQ('redis://localhost/0?name=test')
    rq.put('TEST测试XXXabc12345*@')
    print(rq.get(timeout=1))
    print('task: {}'.format(repr(t)))
    rq.put(dict(t))
    print(Task(**rq.get(timeout=1)))
