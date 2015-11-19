#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: fetcheri.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-06 20:55
#
from gevent import sleep, idle
from gevent.monkey import patch_all, patch_thread, patch_socket
from gevent.queue import Queue

from pythunder.rpc import CallbackObject
from pythunder.libs.fdws import DownloaderManager
from pythunder.rpc import BaseServant, Job
from rpc.interfaces import Fetcher

# patch_all()


class LocalJob(Job):
    def __init__(self, cb, dws=None, pid=None, action=None):
        self._pid = pid
        self._dws = dws
        self._action = action
        super(LocalJob, self).__init__(cb)

    def execute(self):
        getattr(self._dws, self._action)()
        self._cb.ice_response(self._dws.started, self._dws.started)


class BaseFetcherI(Fetcher, BaseServant):
    """

    """
    def __init__(self, properties):
        Fetcher.__init__(self)
        BaseServant.__init__(self, properties)
        self._projects = dict()
        self._dws = DownloaderManager('redis://localhost/0?name=test')
        self._queue = Queue()

    def startProject_async(self, cb, pid, current=None):
        self.workerQueue.put(LocalJob(cb, pid=pid, dws=self._dws, action='start'))

    def holdProject_async(self, cb, pid, current=None):
        self.workerQueue.put(LocalJob(cb, pid=pid, dws=self._dws, action='hold'))

    def resumeProject_async(self, cb, pid, current=None):
        self.workerQueue.put(LocalJob(cb, pid=pid, dws=self._dws, action='resume'))

    def stopProject_async(self, cb, pid, current=None):
        self.workerQueue.put(LocalJob(cb, pid=pid, dws=self._dws, action='stop'))
