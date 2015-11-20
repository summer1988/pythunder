#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: dbredis.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-14 06:42
#

import time

import rom
import six

from rom.util import set_connection_settings

from pythunder import PyThunderBase
from pythunder.utils.miscs import getMd5


class Task(rom.model.Model):
    """

    """
    CREATED = 0x0030
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
    priority = rom.Integer(default=0)
    updateTime = rom.Float(default=0)
    executeTime = rom.Float(default=0)
    expireTime = rom.Integer(default=0)
    tries = rom.Integer(default=0)
    retry = rom.Integer(default=3)
    status = rom.Integer(default=CREATED)
    ok = rom.Boolean(default=False)

    @classmethod
    def fromDict(cls, obj):
        obj.pop('id', None)
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
    DELAYDELETE = 7

    id = rom.PrimaryKey()
    md5Hash = rom.String(index=True, keygen=rom.FULL_TEXT)
    startUrl = rom.String(default='')
    source = rom.Text(unique=True, required=True)
    updateTime = rom.Float(default=0)
    executeTime = rom.Float(default=0)
    delayDelete = rom.Boolean(default=True)
    deleteTick = rom.Json()
    tasks = rom.ManyToOne(Task, on_delete='restrict')
    status = rom.Integer(default=READY)

    @classmethod
    def from_dict(cls, obj):
        obj.pop('id', None)
        return cls(**obj)


class ProjectManager(PyThunderBase):
    """

    """
    def __init__(self, url):
        self._projects = dict()
        self._changed = True

    def createProject(self, prj):
        project = Project(status=Project.READY, updateTime=time.time(),
                          source='', startUrl='')
        self._checkAndApplyChanges(project, prj)
        project.save()
        self._changed = True
        return project.id

    def startProject(self, pid):
        return self.changeProjectStatus(pid, Project.RUNNING)

    def checkingProject(self, pid):
        return self.changeProjectStatus(pid, Project.CHECKING)

    def stopProject(self, pid):
        return self.changeProjectStatus(pid, Project.STOP, other={'executeTime': time.time()})

    def holdProject(self, pid):
        return self.changeProjectStatus(pid, Project.HOLD)

    def deleteProject(self, pid, delay=60 * 60):
        if delay:
            return self._changeProjectStatus(
                    pid, Project.DELAYDELETE,
                    other={'delayTick': {'time': time.time(), 'delay': delay}}
            )
        else:
            if self._getProject(pid):
                self._getProject(pid).delete()
                self.logger.debug('delete project: {} immediately.'.format(pid))
                return True
            else:
                self.logger.debug('delte project: {} failed'.format(pid))
                return False

    def updateProject(self, pid, **kwargs):
        if 'id' not in kwargs:
            kwargs.setdefault('id', pid)
        return self._updateProject(kwargs)

    def getProjects(self, pidList, dictObj=False):
        if self._changed:
            return self._getProjectFromDB(pidList, dictObj)
        else:
            if dictObj:
                return [self._getProject(pid).to_dict() for pid in pidList if self._getProject(pid)]
            else:
                return [self._getProject(pid) for pid in pidList if self._getProject(pid)]

    def getAllProjects(self, dictObj=False):
        if self._changed:
            return self._getProjectFromDB(dictObj=dictObj)
        else:
            if dictObj:
                return [prj.to_dict() for prj in six.itervalues(self._projects)]
            else:
                return [prj for prj in six.itervalues(self._projects)]

    def changeProjectStatus(self, pid, status, other=None):
        if self._getProject(pid):
            if self._getProject(pid) != status:
                return self._changeProjectStatus(pid, status, other=other)
            else:
                self.logger.debug('project: {} already in status: {}'.format(pid, status))
                return True
        return False

    def _changeProjectStatus(self, pid, status, other=None):
        obj = {'id': pid, 'status': status, 'updateTime': time.time()}
        if self._getProject(pid).status == Project.DELAYDELETE:
            obj.update({'delayTick': {}})
        if other:
            obj.update(other)
        try:
            obj.pop('id', None)
            self._updateProject(obj)
            self._changed = True
            return True
        except:
            self.logger.debug('change project: {} status error'.format(pid), exc_info=True)

    def _updateProject(self, prj):
        pid = prj.get('id')
        if pid and self._getProject(pid):
            self._checkAndApplyChanges(self._getProject(pid), prj)
            self._getProject(pid).save(force=True)
            self.logger.debug('update project: {} --> {}'.format(pid, prj.keys()))
            self._changed = True
            return True
        return False

    def _getProject(self, pid):
        if self._projects.get(pid):
            return self._projects.get(pid)
        else:
            self.logger.debug('project: {} not exists'.format(pid))
            return False

    def _getProjectFromDB(self, pidList=None, dictObj=False):
        if pidList:
            projList = Project.get(pidList)
        else:
            projList = Project.query.filter().all()
        for prj in projList:
            self._projects[prj.id] = prj
        self._changed = False
        if dictObj:
            return [prj.to_dict() for prj in projList]
        else:
            return projList

    @staticmethod
    def _checkAndApplyChanges(orig, other):
        if 'source' in other:
            source = other.pop('source')
            other.pop('md5Hash', None)
            newHash = getMd5(getMd5(source))
            if orig.md5Hash != newHash:
                orig.source = source
                orig.md5Hash = newHash
        for attr, value in six.iteritems(other):
            setattr(orig, attr, value)

if __name__ == '__main__':
    set_connection_settings(db=7)
    isProject = False
    if isProject:
        a = {'md5Hash': '998889', 'source': 'xxx', 'startUrl': ''}
        pm = ProjectManager('')
        print(pm.createProject(a))
        print(pm.getAllProjects())
        ps = list(pm._projects.keys())
        print(pm._projects)

        # print('-->Ps:{}'.format(ps))
        # print(pm.deleteProject(ps[0], delay=None))
    else:
        # task = Task(url='http://www.baidu.com')
        # print(task.save())
        taskList = Task.query.filter().all()
        taskList[0].md5Hash = getMd5(taskList[0].url)
        taskList[0].save()
        print(taskList[0].to_dict())
        pm = ProjectManager('')
        ps = pm.getAllProjects()[0]
        print(ps)
        print('project: {}'.format(ps.to_dict()))
        print(pm.updateProject(ps.id, tasks=[taskList[0]]))
        print(pm.getProjects([27], True))
