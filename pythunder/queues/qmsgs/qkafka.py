#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName: qkafka.py
# Author  : summer1988 (wuzhonghua2734@gmail.com)
# DateTime: 2015-11-09 16:53
#

import codecs

import six
import umsgpack

from gevent import Timeout, sleep
from kafka import KafkaConsumer, KafkaClient, KeyedProducer
from six.moves.urllib_parse import urlparse, parse_qsl

from pythunder.queues.qmsgs import MQBase


urlOptMaps = {
    'autoCommit': ('auto_commit_enable', bool),
    'autoCommitMs': ('auto_commit_interval_ms', int),
    'autoCommitCnt': ('auto_commit_interval_messages', int),
    'maxSize': ('fetch_message_max_bytes', int),
    'minSize': ('fetch_min_bytes', int),
    'group': ('group_id', str),
    'hosts': ('bootstrap_servers', str),
    'timeout': ('socket_timeout_ms', int),
    'client': ('client_id', str)
}


class Producer(KeyedProducer):
    """

    """
    def __init__(self, hosts, client_id, timeout):
        self._client = KafkaClient(['localhost:9092'])
        self._client = KafkaClient(hosts, client_id=client_id, timeout=timeout)
        super(Producer, self).__init__(self._client)

    def close(self):
        try:
            self._client.close()
        except:
            pass


class KafkaMQ(MQBase):
    """
    kafka://sparkh1:9092,sparkh2:9092,sparkh3:9092?topics=xx&group_id=xx

    """
    _CLIENT_ID_ = 'PyThunderKafkaMQCli'
    _GROUP_ID_ = 'PyThunderKafkaMQCliGroup'
    maxLowTimeout = 0.1

    def __init__(self, url):
        super(KafkaMQ, self).__init__(url=url)
        consumerKwargs, producerKwargs = self.fromUrl(url)
        self._topic = consumerKwargs.pop('topic', '')
        topics = self._topic.split(',')
        self._consumer = KafkaConsumer(*topics, **consumerKwargs)
        self._producer = Producer(**producerKwargs)

    def qsize(self):
        try:
            with Timeout(seconds=self.maxLowTimeout, exception=None, ):
                print('no offsets: {}'.format(self._get(noCommit=True)))
        except:
            pass
        localOffsets = self._consumer.offsets()
        return localOffsets

    def _get(self, noCommit=False):
        with Timeout(seconds=self.maxLowTimeout, exception=self.Empty):
            kafkaMessage = self._consumer.next()
            if noCommit:
                return kafkaMessage
            if kafkaMessage:
                try:
                    return kafkaMessage.value
                finally:
                    self._commit(kafkaMessage)
            else:
                raise self.Empty

    def _put(self, item):
        with Timeout(seconds=self.maxLowTimeout, exception=self.Full):
            status = self._producer.send_messages(self._topic, None, *[item])
            if status:
                return 10

    def _commit(self, message):
        try:
            self._consumer.task_done(message)
            self._consumer.commit()
        except:
            pass

    def close(self):
        try:
            del self._consumer
            self._producer.close()
            del self._producer
        except:
            pass

    def fromUrl(self, url):
        urlInfo = urlparse(url)
        qs = urlInfo.query and urlInfo.query or ''
        kwargs = dict()
        options = dict()

        options['hosts'] = urlInfo.netloc
        options['topic'] = urlInfo.path.strip('/')
        for name, value in six.iteritems(dict(parse_qsl(qs))):
            if value:
                options[name] = value
        self.maxSize = options.pop('maxSize', 10000)
        self.lazyLimit = options.pop('lazyLimit', True)
        options.setdefault('group', self._GROUP_ID_ + '-{}'.format(id(self)))
        # options.setdefault('group')
        options.setdefault('client', self._CLIENT_ID_)
        if urlInfo.scheme != 'kafka':
            raise AttributeError('schema {} not supported'.format(urlInfo.scheme))
        else:
            for name, value in six.iteritems(options):
                mirror = urlOptMaps.get(name)
                if mirror:
                    value = mirror[1](value)
                    if mirror == 'bootstrap_servers':
                        value = value.split(',')
                    kwargs[mirror[0]] = value
                else:
                    kwargs[name] = value
        return kwargs, {
            'hosts': options.pop('hosts', '').split(','),
            'client_id': options.pop('client_id', self._CLIENT_ID_),
            'timeout': options.pop('timeout', 120)
        }


if __name__ == '__main__':
    from gevent.monkey import patch_all

    patch_all()

    mq = KafkaMQ('kafka://localhost:9092/test?autoCommit=true&group=TESTBIG')
    mq2 = KafkaMQ('kafka://localhost:9092/test?autoCommit=true&group=TESTBIG')

    for i in six.moves.range(2):
        mq.put('xx测试消息-{}'.format('hhhXX'))
    # for i in six.moves.range(1):
    #     try:
    #         print('[{}] - '.format(i) + mq.get(timeout=10), 'utf-8')
    #     except:
    #         pass
    # print('mq2-get:{}'.format(mq2.get()))
    print(mq.get(timeout=1))
    print(mq.qsize())
    print(mq2.qsize())
    print(mq2.get(timeout=1))
    print(mq2.qsize())

