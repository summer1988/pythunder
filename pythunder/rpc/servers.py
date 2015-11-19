#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: servers.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-12 17:29
#

from pythunder.rpc import BaseServer
from pythunder.rpc.impls.fetcheri import BaseFetcherI


class FetcherServer(BaseServer):
    cls = BaseFetcherI
