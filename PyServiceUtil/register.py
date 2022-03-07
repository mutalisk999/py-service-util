#!/usr/bin/env python
# encoding: utf-8

import time
import logging
import threading
import grpc  # type: ignore

from client import V3Client  # type: ignore
from etcd3.exceptions import Etcd3Exception  # type: ignore


class RegSvcClient(object):
    def __init__(self, end_points=None, ca_cert=None,
                 cert_key=None, cert_cert=None, timeout=None, user=None,
                 password=None):
        self.client = V3Client(end_points=end_points, ca_cert=ca_cert,
                               cert_key=cert_key, cert_cert=cert_cert, timeout=timeout, user=user,
                               password=password)
        self.run_flag = True
        self.logger = logging

    def _dispose(self):
        self.client.close()

    def stop(self):
        self.run_flag = False

    def set_logger(self, logger):
        self.logger = logger

    def register_service(self, keep_alive: int, service_ttl: int, key_prefix: str, svc_id: str, svc_name: str,
                         svc_address: str, logger):
        key_prefix = "/etcd_services" if key_prefix == "" else key_prefix
        keep_alive = 5 if keep_alive == 0 else abs(keep_alive)
        service_ttl = 30 if service_ttl == 0 else abs(service_ttl)

        self.set_logger(logger)

        try:
            lease = self.client.lease(ttl=service_ttl)
            key = "/".join([key_prefix, svc_id, svc_name])
            self.client.put(key=key, value=svc_address.encode("utf8"), lease=lease)
        except Etcd3Exception as exc:
            print("Etcd3Exception:", str(exc))
            raise exc

        def thread_callback(args: RegSvcClient):
            while True:
                if not args.run_flag:
                    args._dispose()
                    args.logger.info("[Cancel] keep alive at %s", time.asctime())
                    break
                try:
                    args.logger.info("keep alive request at %s", time.asctime())
                    resp = lease.refresh()
                    args.logger.info("keep alive response %s at %s", str(resp).replace("\n", ""), time.asctime())
                except grpc.RpcError as exc:
                    args.logger.info("[RpcError] keep alive at %s", time.asctime())
                    break
                except Etcd3Exception as exc:
                    args.logger.info("[Etcd3Exception] keep alive at %s", time.asctime())
                    break

                time.sleep(keep_alive)

        thread_id = threading.Thread(target=thread_callback, args=(self,))
        thread_id.setDaemon(True)
        thread_id.start()
