#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: miscs.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-09 14:26
#

import sys

import six

from hashlib import md5


def getMd5(strObj):
    if six.PY3:
        # if type(strObj) == six.string_types:
        #     strObj = strObj.encode('utf-8')
        if type(strObj) == six.text_type:
            strObj = strObj.encode('utf-8')
    return md5(strObj).hexdigest()


def getHtmlSize(html):
    try:
        length = sys.getsizeof(html)
        mainPart, leftPart = divmod(length, 1024)
        if mainPart <= 0:
            return '{}'.format(leftPart), 'bytes'
        else:
            return '{}'.format(round(length / 1024.0, 3)), 'kb'
    except:
        return '0', 'bytes'
