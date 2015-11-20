#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: __init__.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-09 14:12
#

import time

import umsgpack

from six.moves import queue as BaseQueue
from gevent import sleep


# class MQCliBase(object):
#     cls = None
#
#     def __init__(self, *args, **kwargs):
#         self._withLock = kwargs.pop('withLock', False)
#         self._lock = Lock()
#         if isinstance(self.cls[0], (tuple, list)):
#             self._receiver = self.cls[0][0](*args, **self._parseParams2Cfg(self.cls[0][1], **kwargs))
#             self._recvFuncName = self.cls[0][2]
#             self._recvFuncKwargs = self.cls[0][3]
#             self._sender = self.cls[1][0](**self._parseParams2Cfg(self.cls[1][1], **kwargs))
#             self._sendFuncName = self.cls[1][2]
#             self._sendFuncKwargs = self.cls[1][3]
#         else:
#             self._client = self.cls[0](**self._parseParams2Cfg(self.cls[1], **kwargs))
#             self._recvFuncName = self.cls[2]
#             self._recvFuncKwargs = self.cls[3]
#             self._sendFuncName = self.cls[4]
#             self._sendFuncKwargs = self.cls[5]
#
#     def _send(self, *args, **kwargs):
#         return getattr(self._getClient(sender=True), self._sendFuncName)(*args)
#
#     def _receive(self, *args, **kwargs):
#         return getattr(self._getClient(), self._recvFuncName)(
#             **self._parseParams2Cfg(self._recvFuncKwargs, **kwargs)
#         )
#
#     def _getClient(self, sender=False):
#         if hasattr(self, '_client'):
#             return self._client
#         else:
#             return sender and self._sender or self._receiver
#
#     def send(self, **kwargs):
#         if self.withLock:
#             with self._lock:
#                 self._send(**kwargs)
#         else:
#             self._send(**kwargs)
#
#     def receive(self, **kwargs):
#         if self.withLock:
#             with self._lock:
#                 return self._receive(**kwargs)
#         else:
#             return self._receive(**kwargs)
#
#     def _parseParams2Cfg(self, defaultOpts, **kwargs):
#         config = {}
#         for key in defaultOpts:
#             if key in kwargs:
#                 config[key] = kwargs.pop(key)
#             else:
#                 config[key] = defaultOpts[key]
#         return config
#
#     def close(self):
#         try:
#             if hasattr(self._getClient(), 'close'):
#                 self._getClient().close()
#             if hasattr(self._getClient(), 'stop'):
#                 self._getClient().stop()
#             if hasattr(self._getClient(sender=True), 'close'):
#                 self._getClient(sender=True).close()
#             if hasattr(self._getClient(sender=True), 'stop'):
#                 self._getClient(sender=True).stop()
#             try:
#                 if hasattr(self, '_client'):
#                     del self._client
#                 if hasattr(self, '_sender'):
#                     del self._sender
#                 if hasattr(self, '_receiver'):
#                     del self._receiver
#             except:
#                 pass
#         except:
#             pass
#
#     def __del__(self):
#         self.close()
#
#     @property
#     def withLock(self):
#         return self._withLock


class MQBase(object):
    """
    BaseMessageQueue for message consume.
    """
    Empty = BaseQueue.Empty
    Full = BaseQueue.Full

    defaultUrl = ''

    def __init__(self, *args, **kwargs):
        self._url = kwargs.pop('url', self.defaultUrl)
        self.lastQsize = 0
        self.maxSize = 10000
        self.lazyLimit = True

    def get(self, block=True, timeout=None):
        if not block:
            return self.get_nowait()
        start = time.time()
        while True:
            try:
                return self.get_nowait()
            except self.Empty:
                if timeout:
                    lasted = time.time() - start
                    if timeout > lasted:
                        sleep(min(0.03, timeout - lasted))
                    else:
                        raise
                else:
                    sleep(0.03)

    def put(self, item, block=True, timeout=None):
        if not block:
            return self.put_nowait(item=item)
        start = time.time()
        while True:
            try:
                return self.put_nowait(item=item)
            except self.Empty:
                if timeout:
                    lasted = time.time() - start
                    if timeout > lasted:
                        sleep(min(0.03, lasted - start))
                    else:
                        raise
                else:
                    sleep(0.03)

    def get_nowait(self):
        ret = self._get()
        if ret is None:
            raise self.Empty
        return umsgpack.unpackb(ret)

    def put_nowait(self, item):
        if (not self.lazyLimit or self.lastQsize >= self.maxSize) \
                and self.full():
            raise self.Full
        ret = self._put(item=umsgpack.packb(item))
        if ret is not None:
            self.lastQsize = ret
        return ret

    def _get(self, *args, **kwargs):
        raise NotImplementedError

    def _put(self, *args, **kwargs):
        raise NotImplementedError

    def qsize(self):
        raise NotImplementedError

    def empty(self):
        return self.qsize() == 0

    def full(self):
        return self.maxSize and self.qsize() >= self.maxSize

    def close(self):
        pass

    def fromUrl(self, url):
        pass

    def __del__(self):
        try:
            self.close()
        except:
            pass
