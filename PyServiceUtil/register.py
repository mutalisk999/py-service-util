#!/usr/bin/env python
# encoding: utf-8

import sys
import time
import logging
import threading
import grpc  # type: ignore
from client import V3Client  # type: ignore
from random import randint
from etcd3.leases import Lease  # type: ignore
from etcd3.transactions import Put  # type: ignore
from etcd3.exceptions import Etcd3Exception


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

        lease = Lease(randint(1000000, 2000000), service_ttl, self.client)

        key = "/".join([key_prefix, svc_id, svc_name])
        Put(key=key, value=svc_address, lease=lease)

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
                    args.logger.info("[Cancel] keep alive at %s", time.asctime())
                    break
                except Etcd3Exception as exc:
                    print("Etcd3Exception:", str(exc))
                    break

                time.sleep(keep_alive)

        thread_id = threading.Thread(target=thread_callback, args=(self,))
        thread_id.setDaemon(True)
        thread_id.start()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    endpoints = (("127.0.0.1", 12379), ("127.0.0.1", 22379), ("127.0.0.1", 32379))
    cli = RegSvcClient(endpoints)
    cli.register_service(5, 30, "", "test", "key", "value", logging)

    time.sleep(30)
    cli.stop()

    time.sleep(10)
