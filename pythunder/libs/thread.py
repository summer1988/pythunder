#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: thread
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-06 22:57
#

from enum import Enum

from gevent import sleep, kill, idle
from gevent.event import Event
from gevent.monkey import patch_all
from gevent.threading import Thread, Lock

from pythunder import PyThunderBase
from pythunder.libs.signals import threadSig

__all__ = ('ThreadEvent', 'PyThunderThread', 'Group')


class ThreadEvent(Enum):
    READY = 0x0008
    START = 0x0001
    HOLD = 0x0002
    STOP = 0x0003
    RESUME = 0x0004


class Group(object):
    """

    """
    def __init__(self, maxSize=None):
        self._pool = set()
        self._maxSize = maxSize
        self._started = False

    def add(self, _thread):
        if self._maxSize and (len(self._pool) > self._maxSize):
            raise ValueError('out of capacity: {}'.format(self._maxSize))
        self._pool.add(_thread)

    def start(self):
        try:
            if not self.started:
                for _ in self._pool:
                    _.setSignalSender(self)
                threadSig.send(self, event=ThreadEvent.START)
                self._started = True
        except:
            pass

    def resume(self):
        try:
            threadSig.send(self, event=ThreadEvent.RESUME)
        except:
            pass

    def stop(self):
        try:
            threadSig.send(self, event=ThreadEvent.STOP)
            self._started = False
        except:
            pass
        self._pool.clear()

    def hold(self):
        try:
            threadSig.send(self, event=ThreadEvent.HOLD)
        except:
            pass

    def join(self, timeout=None):
        for _ in self._pool:
            try:
                _.join(timeout=0.1)
            except:
                pass
        self._pool.clear()

    @property
    def started(self):
        return self._started

    @property
    def stoped(self):
        return not self._started


class PyThunderThread(Thread, PyThunderBase):
    """

    """
    def __init__(self, group=None, target=None, name=None, daemon=True, sender=None):

        super(PyThunderThread, self).__init__(group=group, name=name, target=None, daemon=daemon)
        self._quit = False
        self._sender = sender and sender or self
        self._startEvent = Event()
        self._holdEvent = Event()
        self._stopEvent = Event()
        self._currEvent = ThreadEvent.READY
        self._lock = Lock()

    def run(self):
        super(PyThunderThread, self).run()

    def start(self):
        with self._lock:
            self.quit = False
            self._currEvent = ThreadEvent.START
        super(PyThunderThread, self).start()

    def stop(self):
        with self._lock:
            self.quit = True
            self._currEvent = ThreadEvent.STOP
            if self.holdEvent.isSet():
                self.holdEvent.clear()
        try:
            threadSig.disconnect(self.eventHandler, sender=self._sender)
            kill(self)
            self.join(timeout=0.1)
        except:
            pass
        return True

    def eventHandler(self, sender, **kwargs):
        event = kwargs.pop('event', None)
        self.logger.debug('thread get event from : {} event: {}'.format(sender, event))
        if event == ThreadEvent.START:
            if self.currEvent == ThreadEvent.READY:
                self.start()
        elif event == ThreadEvent.HOLD:
            with self._lock:
                if self.holdEvent.isSet():
                    self.holdEvent.clear()
                self._currEvent = event
        elif event == ThreadEvent.STOP:
            self.stop()
        elif event == ThreadEvent.RESUME:
            with self._lock:
                self.holdEvent.set()
                self._currEvent = ThreadEvent.START

    def hold(self):
        if self.currEvent == ThreadEvent.HOLD:
            self.holdEvent.wait()

    def setSignalSender(self, sender=None):
        if sender:
            self._sender = sender
        threadSig.connect(self.eventHandler, sender=self._sender)

    @property
    def running(self):
        return not self.quit and self.currEvent != ThreadEvent.STOP

    @property
    def quit(self):
        return self._quit

    @quit.setter
    def quit(self, value):
        self._quit = value

    @property
    def holdEvent(self):
        return self._holdEvent

    @property
    def currEvent(self):
        return self._currEvent

    @property
    def lock(self):
        return self._lock


if __name__ == '__main__':
    class TT(PyThunderThread):

        def run(self):
            while self.running and self.currEvent != ThreadEvent.STOP:
                try:
                    self.hold()
                    print('current: {} {}'.format(self.currEvent, self.holdEvent.isSet()))
                    sleep(1)
                except:
                    pass
    class TT2(PyThunderThread):

        def run(self):
            while self.running:
                try:
                    print('send start to th: {}'.format('xx198'))
                    # threadSig.send('xx198', event=ThreadEvent.START)
                    sleep(1)
                except:
                    pass
    th = TT(sender='xx198')
    tt2 = TT2()
    # tt2.start()
    threadSig.send(sender='xx198', event=ThreadEvent.START)
    sleep(2)
    threadSig.send(sender='xx198', event=ThreadEvent.HOLD)
    sleep(2)
    threadSig.send(sender='xx198', event=ThreadEvent.RESUME)
    sleep(2)
    print('-' * 40)
    group = Group()
    [group.add(TT()) for _ in range(5)]
    group.start()
    # sleep(50)
    print('started---->')
    sleep(5)
    print('will hold --->')
    group.hold()
    sleep(5)
    print('will resume --->')
    group.resume()
    print('will stop -->')
    group.stop()

