#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: __init__.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-06 20:54
#

import Ice

from pythunder.libs.logger import PyThunderLogger
from pythunder.utils.miscs import getMd5


class PyThunderBase(object):
    """

    """

    @property
    def loggerName(self):
        return self.__module__ + '.' + self.__class__.__name__

    @property
    def logger(self):
        if not hasattr(self, '__logger'):
            self.__logger = PyThunderLogger(self.loggerName)
            Ice.setProcessLogger(self.__logger)
            # PyThunderLogger.basicConfig(self.loggerName)
        return self.__logger


taskDefaults = {
    'id': getMd5('id'), 'url': 'http://www.qq.com',
    'pid': getMd5('pid'), 'priority': 0,
    # 'fetch': {}, 'schedule': {}, 'process': {}, 'filter': {}, 'track': {},
    'updateTime': 0, 'executeTime': 0, 'ok': False
}


class Task(dict):
    """

    """
    __slots__ = ('id', 'pid', 'url', 'priority', 'fetch', 'schedule',
                 'collect', 'process', 'filter', 'executeTime',
                 'updateTime', 'track', 'ok')

    def __init__(self, **kwargs):
        self._checkAttrs(kwargs)
        super(Task, self).__init__(**kwargs)

    def _checkAttrs(self, kwargs):
        kwargs.pop('iterable', None)
        for attr in taskDefaults:
            kwargs.setdefault(attr, taskDefaults[attr])
        for attr in kwargs:
            if attr not in self.__slots__:
                raise KeyError('attr: {} not supported'.format(attr))

    def keys(self):
        return self.__slots__

    def __setitem__(self, key, value):
        if key not in self.__slots__:
            raise KeyError('attr: {} not supported'.format(key))
        self[key] = value

    def __setattr__(self, key, value):
        if key not in self.__slots__:
            raise KeyError('attr: {} not supported'.format(key))
        self[key] = value

    def __getattr__(self, item):
        return self[item]

    def __len__(self):
        return len(self.__slots__)

    def __cmp__(self, other):
        if self.executeTime > other.executeTime:
            return True
        if self.priority > other.priority:
            return True
        return False

    def __lt__(self, other):
        if self.executeTime > other.executeTime:
            return True
        if self.priority > other.priority:
            return True
        return False


if __name__ == '__main__':
    print('{}'.format(Task()))
    print(isinstance(Task(), dict))