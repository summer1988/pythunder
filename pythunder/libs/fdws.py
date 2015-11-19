#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: fdws
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-06 21:34
#

import sys
import traceback

import six

from gevent import sleep, idle
from gevent.queue import Empty, Queue

from pythunder import PyThunderBase, Task
from pythunder.queues.qmsgs.qredis import RedisMQ
from pythunder.libs.httpclient import DefaultHttpClient
from pythunder.libs.thread import PyThunderThread, Group
from pythunder.utils.miscs import getHtmlSize


class AbcDownloader(PyThunderThread):
    """

    """
    httpClientCls = None

    def __init__(self, qin, qout):
        super(AbcDownloader, self).__init__()
        self._qin = qin
        self._qout = qout
        self._httpClient = self.httpClientCls()

    def fetch(self, task):
        raise NotImplementedError

    @property
    def httpClient(self):
        return self._httpClient


class DefaultDownloader(AbcDownloader):
    """

    """
    httpClientCls = DefaultHttpClient

    def run(self):
        while self.running:
            try:
                self.hold()
            except:
                pass
            try:
                task = self._qin.get(timeout=2)
                task = self.fetch(task)
                self._qout.put(task)
                self.logger.debug('download [task: id:{task.id} pid:{task.pid}'
                                  ' priority:{task.priority} url:{task.url} '
                                  'html page, size: {htmlSize}'.format(
                    task=Task(**task), htmlSize=Task(**task).track['fetch']['htmlSize']))
            except Empty:
                sleep(0)
            except:
                self.logger.warning('download [task: id:{task.id} '
                                    'pid:{task.pid} priority:{task.priority}'
                                    ' url:{task.url}] error.'
                                    .format(task=Task(**task)), exc_info=True)
                sleep(0)

    def fetch(self, task):
        track = task.pop('track', {'fetch': {}})
        resp = None
        fetch = task.pop('fetch', {'method': 'GET', 'timeout': 20})
        track['ok'] = True
        try:
            resp = self.httpClient.request(url=task['url'], **fetch)
            if resp.status_code == 200:
                track['fetch']['htmlSize'] = ''.join(getHtmlSize(resp.content))
                track['fetch']['htmlSimple'] = resp.content[:50]
            else:
                track['ok'] = False
                track['fetch']['ok'] = False
                if 'error' not in track['fetch']:
                    track['fetch']['error'] = dict()
                    track['fetch']['error']['desc'] = resp.reason
                    self.logger.warning('downloader fetch [task: id:{task.id} '
                                        'pid:{task.pid} priority:'
                                        '{task.priority} url:{task.url}'
                                        ' page error'.format(task=task), exc_info=True)
            track['fetch']['status'] = resp.status_code
            track['fetch']['headers'] = dict(resp.headers)
            track['fetch']['cookies'] = resp.cookies.get_dict()
        except:
            track['ok'] = False
            if resp:
                track['fetch']['status'] = resp.status_code
                track['fetch']['headers'] = dict(resp.headers)
                track['fetch']['cookies'] = resp.cookies.get_dict()
            if 'error' not in track['fetch']:
                track['fetch']['error'] = dict()
            ex_cls, ex, tb = sys.exc_info()
            track['fetch']['error']['exc'] = '{}'.format('|'.join(traceback.format_tb(tb)).replace('\n', '|'))
            track['fetch']['error']['desc'] = '{}'.format('. '.join(ex.args))
            del ex_cls, ex, tb
            self.logger.warning('downloader fetch [task: id:{task.id} pid:'
                                '{task.pid} priority:{task.priority} url:'
                                '{task.url} page error'
                                .format(task=Task(**task)), exc_info=True)
        task['fetch'] = fetch
        task['track'] = track
        del track, fetch
        return task


class MQLocalWorker(PyThunderThread):
    """

    """

    def __init__(self, inq, outq, sender=None):
        self._mq = inq
        self._outq = outq
        super(MQLocalWorker, self).__init__(sender=sender)

    def run(self):
        while self.running:
            try:
                self.hold()
            except:
                pass
            try:
                task = self._mq.get(timeout=2)
                self.logger.debug('get task from queue: {task.id} {task.url}'.format(task=Task(**task)))
                self._outq.put(task)
            except KeyboardInterrupt:
                pass
            except Empty:
                sleep(0)
            except Exception as e:
                self.logger.warning('{} error occurt. ', exc_info=True)
                sleep(0)


class DownloaderManager(PyThunderBase):
    """

    """

    def __init__(self, mqUrl, mqCls=None, dlCls=None, maxSize=5):
        self._maxSize = maxSize
        self._mqCls = mqCls and mqCls or RedisMQ
        self._dls = Group()
        self._mqInWorkers = Group()
        self._mqOutWorkers = Group()
        self._mqin = self._mqCls(mqUrl)
        self._mqout = self._mqCls(mqUrl + '&suffix=HTML')
        self._inq = Queue(15)
        self._outq = Queue(15)
        self._dlCls = dlCls and dlCls or DefaultDownloader

    def start(self):
        [self._dls.add(self._dlCls(self._inq, self._outq)) for _ in six.moves.range(self._maxSize)]
        [self._mqOutWorkers.add(MQLocalWorker(self._outq, self._mqout)) for _ in six.moves.range(self._maxSize - 3)]
        [self._mqInWorkers.add(MQLocalWorker(self._mqin, self._inq)) for _ in six.moves.range(self._maxSize - 3)]
        self.executeGroup('start')

    def stop(self):
        self.executeGroup('stop')

    def hold(self):
        self.executeGroup('hold')

    def resume(self):
        self.executeGroup('resume')

    def executeGroup(self, action):
        if action in ('resume', 'start'):
            getattr(self._dls, action)()
            getattr(self._mqOutWorkers, action)()
            getattr(self._mqInWorkers, action)()
        else:
            getattr(self._mqInWorkers, action)()
            getattr(self._dls, action)()
            getattr(self._mqOutWorkers, action)()

    def __del__(self):
        try:
            self.stop()
        except:
            pass

    @property
    def started(self):
        return self._mqInWorkers.started and self._mqOutWorkers.started and self._dls.started

__all__ = ('AbcDownloader', 'DefaultDownloader')


if __name__ == '__main__':
    from gevent import sleep
    from gevent.monkey import patch_all
    from pythunder import Task

    patch_all()
    # q = RedisMQ('redis://localhost/0?name=test')
    # [q.put(Task(url='http://www.qq.com')) for _ in six.moves.range(100)]
    dwm = DownloaderManager('redis://localhost/0?name=test')
    dwm.logger.debug('start dwm ...')
    dwm.start()
    sleep(15)
    dwm.logger.debug('hold dwm ..')
    dwm.hold()
    sleep(25)
    dwm.logger.debug('resume dwm ...')
    dwm.resume()
    sleep(25)
    dwm.logger.debug('stop dwm ...')
    dwm.stop()
    sleep(2)