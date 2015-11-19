#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: dmongo.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-18 16:51
#

from django.db import models
from jsonfield import JSONField


class TaskModel(models.Model):
    id = models.CharField(primary_key=True, unique=True)
    md5Hash = models.CharField()
    url = models.CharField()
    fetch = JSONField()
    schedule = JSONField()
    filter = JSONField()
    collect = JSONField()
    process = JSONField()
    track = JSONField()
    updateTime = models.FloatField(default=0)
    executeTime = models.FloatField(default=0)
    tries = models.FloatField(default=0)
    retry = models.FloatField(default=3)
    ok = models.BooleanField(default=False)


class ProjectModel(models.Model):
    id = models.CharField(primary_key=True, unique=True)
    md5Hash = models.CharField()
    startUrl = models.CharField()
    source = models.TextField()
    updateTime = models.FloatField(default=0)
    executeTime = models.FloatField(default=0)
    expireTime = models.IntegerField(default=0)
    delayDelte = models.BooleanField(default=True)
    tasks = models.ManyToOneRel()

