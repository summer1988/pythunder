#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: logger.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-06 21:35
#

import logging

import Ice

__all__ = ('PyThunderLogger', )


class OneLineExceptionFormatter(logging.Formatter):

    def formatException(self, exc_info):
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result)

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        return record.exc_text and s.replace('\n', '') + '|' or s


class PyThunderLogger(logging.Logger, Ice.Logger):
    """

    """
    DEFAULT_LOG_FORMAT = '%(asctime)s : %(levelname)s : %(processName)s : ' \
                         '%(threadName)s : %(name)s : %(funcName)s ' \
                         '[%(lineno)sL] : %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, name, level=logging.DEBUG):
        Ice.Logger.__init__(self)
        logging.Logger.__init__(self, name, level)
        self.basicConfig(self.name)

    def trace(self, category, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, msg, args, **kwargs)

    def configure(self):
        pass

    def basicConfig(self, name=None, enableOneline=False):
        hdl = logging.StreamHandler()
        # fmt = OneLineExceptionFormatter(self.DEFAULT_LOG_FORMAT, self.DEFAULT_DATE_FORMAT)
        fmt = logging.Formatter(self.DEFAULT_LOG_FORMAT, self.DEFAULT_DATE_FORMAT)
        hdl.setFormatter(fmt)
        # root = logging.getLogger()
        self.setLevel(logging.DEBUG)
        self.addHandler(hdl)


if __name__ == '__main__':
    logger = PyThunderLogger('test')
    # logger.basicConfig(logger.name)
    logger.debug('asdfkasldfjasdlf')