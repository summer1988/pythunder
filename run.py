#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: run.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-12 17:31
#

from gevent.monkey import patch_all, patch_socket, patch_thread, patch_time

from pythunder.rpc.servers import FetcherServer

# patch_all()
patch_thread()
patch_socket()
patch_time()

FetcherServer.serveForever()
