#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: __init__.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-06 20:55
#

import sys

import Ice
import six

from gevent import sleep
from gevent.queue import Queue, Empty

from pythunder import PyThunderBase
from pythunder.libs.signals import threadSig
from pythunder.libs.thread import PyThunderThread, ThreadEvent


class BaseServant(PyThunderBase):
    """

    """
    def __init__(self, properties):
        super(BaseServant, self).__init__()
        self._properties = properties
        self._servantPrefix = self._properties.getProperty('Servant.Config.Prefix')
        self._servantConfig = self._properties.getPropertiesForPrefix(self._servantPrefix)
        self._workerQueue = None

    @property
    def servantConfig(self):
        return self._servantConfig

    @property
    def properties(self):
        return self._properties

    @property
    def workerQueue(self):
        return self._workerQueue

    @workerQueue.setter
    def workerQueue(self, value):
        self._workerQueue = value


class Worker(PyThunderThread):
    def __init__(self):
        super(Worker, self).__init__()
        self._queue = Queue()

    def run(self):
        while self.running:
            try:
                self.hold()
            except:
                pass
            try:
                job = self._queue.get(timeout=1)
                job.execute()
            except Empty:
                sleep(0)
            except:
                self.logger.warning('error occurt in worker', exc_info=True)
                sleep(0)

    def stop(self):
        super(Worker, self).stop()
        with self._lock:
            self._queue = Queue()

    @property
    def workerQueue(self):
        return self._queue


class BaseServer(Ice.Application, PyThunderBase):
    """

    """
    cls = None

    def getAdapterName(self, properties):
        for key, value in six.iteritems(properties.getPropertiesForPrefix('')):
            if '.AdapterId' in key:
                return key.split('.')[0]

    def run(self, args):
        self.callbackOnInterrupt()
        worker = Worker()
        worker.setSignalSender(worker)
        properties = self.communicator().getProperties()
        adapterName = self.getAdapterName(properties)
        adapter = self.communicator().createObjectAdapter(adapterName)
        _id = self.communicator().stringToIdentity(properties.getProperty("Identity"))
        servant = self.cls(properties)
        servant.workerQueue = worker.workerQueue
        adapter.add(servant, _id)
        threadSig.send(worker, event=ThreadEvent.START)
        adapter.activate()
        self.communicator().waitForShutdown()
        if self.interrupted():
            threadSig.send(worker, event=ThreadEvent.STOP)
            self.logger.warning('{} terminated !'.format(self.appName))
        return 0

    @classmethod
    def serveForever(cls):
        sys.exit(cls().main(sys.argv))

    def interruptCallback(self, sig):
        self._communicator.shutdown()


class CallbackObject(object):

    def ice_response(self, *args, **kwargs):
        raise NotImplementedError

    def ice_exception(self, ex):
        raise NotImplementedError


class Job(object):
    def __init__(self, cb, *args, **kwargs):
        self._cb = cb
        for _ in kwargs:
            setattr(self, _, kwargs[_])

    def execute(self):
        raise NotImplementedError