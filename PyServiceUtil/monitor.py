#!/usr/bin/env python
# encoding: utf-8
import logging
import threading
import time

from threading import Lock

from etcd3 import Etcd3Exception
from etcd3.events import PutEvent, DeleteEvent  # type: ignore
from client import V3Client  # type: ignore


class MonSvcClient(object):
    def __init__(self, end_points=None, ca_cert=None,
                 cert_key=None, cert_cert=None, timeout=None, user=None,
                 password=None):
        self.client = V3Client(end_points=end_points, ca_cert=ca_cert,
                               cert_key=cert_key, cert_cert=cert_cert, timeout=timeout, user=user,
                               password=password)
        self.cancel = None
        self.logger = logging
        self.lock = Lock()
        self.service_map = {}

    def _dispose(self):
        self.client.close()

    def stop(self):
        if self.cancel is not None:
            self.logger.info("[Cancel] watcher at %s", time.asctime())
            self.cancel()

    def set_logger(self, logger):
        self.logger = logger

    def monitor_service(self, key_prefix: str, logger, put_callback, delete_callback):
        key_prefix = "/etcd_services/test/key" if key_prefix == "" else key_prefix
        self.set_logger(logger)

        try:
            kvs = list(self.client.get_prefix(key_prefix=key_prefix))
        except Etcd3Exception as exc:
            print("Etcd3Exception:", str(exc))
            raise exc

        with self.lock:
            for (v, meta) in kvs:
                key = meta.key.decode("utf8")
                val = v.decode("utf8")
                self.service_map[key] = val

                if put_callback is not None:
                    put_callback(key, val)

        def thread_callback(events_iterator, logger, put_callback, delete_callback):
            for event in events_iterator:
                if isinstance(event, PutEvent):
                    with self.lock:
                        key = event.key.decode("utf8")
                        val = event.value.decode("utf8")
                        self.service_map[key] = val

                        if put_callback is not None:
                            put_callback(key, val)
                        logger.info("service watcher put %s | %s at %s", key, val, time.asctime())
                elif isinstance(event, DeleteEvent):
                    with self.lock:
                        key = event.key.decode("utf8")
                        del self.service_map[key]

                        if delete_callback is not None:
                            delete_callback(key)
                        logger.info("service watcher delete %s at %s", key, time.asctime())
                else:
                    pass

        events_iterator, self.cancel = self.client.watch_prefix(key_prefix=key_prefix)
        thread_id = threading.Thread(target=thread_callback,
                                     args=(events_iterator, logger, put_callback, delete_callback))
        thread_id.setDaemon(True)
        thread_id.start()
