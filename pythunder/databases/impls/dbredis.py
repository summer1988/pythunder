#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: dbredis.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-14 06:42
#

import rom
import six

from rom.util import set_connection_settings

from pythunder import PyThunderBase
from pythunder.utils.miscs import getMd5


class Task(rom.model.Model):
    """

    """
    QUEUED = 0x0001
    ONFETCH = 0x0002
    FILTERING = 0x0004
    ONPROCESS = 0x0008
    ONCOLLECT = 0x0010
    FAILED = 0x0020
    SUCCESS = 0x0040

    id = rom.PrimaryKey(index=True)
    md5Hash = rom.String()
    url = rom.String(required=True, unique=True)
    fetch = rom.Json()
    schedule = rom.Json()
    filter = rom.Json()
    collect = rom.Json()
    process = rom.Json()
    track = rom.Json()
    updateTime = rom.Float(required=True, default=0)
    executeTime = rom.Float(required=True, default=0)
    expireTime = rom.Integer(default=0)
    tries = rom.Integer(required=True, default=0)
    retry = rom.Integer(required=True, default=3)
    ok = rom.Boolean(required=True, default=False)

    @classmethod
    def fromDict(cls, obj):
        return cls(**obj)


class Project(rom.model.Model):
    """

    """
    READY = 0
    CHECKING = 1
    DEBUG = 2
    RUNNING = 3
    HOLD = 4
    IDLE = 5
    STOP = 6

    id = rom.PrimaryKey()
    md5Hash = rom.String(unique=True, index=True, keygen=rom.FULL_TEXT)
    startUrl = rom.String(default='http://localhost/test.html')
    source = rom.Text(required=True)
    updateTime = rom.Float(required=True, default=0)
    executeTime = rom.Float(required=True, default=0)
    delayDelte = rom.Boolean(default=True)
    status = rom.String(default=0)

    @classmethod
    def from_dict(cls, obj):
        return cls(**obj)


class ProjectManager(PyThunderBase):
    """

    """
    def __init__(self, url):
        self._projects = dict()

    def updateProject(self, prj):
        pass

    def createProject(self, prj):
        pass

    def deleteProject(self, pid):
        pass

    def getProject(self, pidList):
        pass

    def getAllProject(self):
        pass

    def _getProject(self, pid):
        return self._projects.get(pid)

    @staticmethod
    def _checkChanges(orig, other):
        if 'source' in other:
            source = other.pop('source')
            other.pop('md5Hash', None)
            newHash = getMd5(getMd5(source))
            if orig.md5Hash != newHash:
                orig.source = source
                orig.md5Hash = newHash
        for attr, value in six.iteritems(other):
            pass




if __name__ == '__main__':
    set_connection_settings(db=7)
    a = {'md5Hash': '8889'}
    prj = Project(md5Hash='9999', source='')
    # sid = prj.save()
    # print('dproj: {}'.format(sid))
    prjList = prj.query.filter().all()
    prjList[0].md5Hash = '8889'
    prjList[0].save()
    for _ in prjList:
        print(_.to_dict())
        # _.delete()