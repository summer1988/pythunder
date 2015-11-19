#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: scheduleri.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-13 11:36
#

from pythunder.rpc import BaseServant
from rpc.interfaces import Scheduler

class SchedulerI(Scheduler, BaseServant):
    """

    """
    def __init__(self, properties):
        Scheduler.__init__(self)
        BaseServant.__init__(self, properties)

    def startProject(self, pid, current=None):
        pass

    def holdProject(self, pid, current=None):
        pass

    def resumeProject(self, pid, current=None):
        pass

    def stopProject(self, pid, current=None):
        pass