#!/usr/bin/env python
# encoding: utf-8

from .client import V3Client  # type: ignore


class MonSvcClient(object):
    def __init__(self, endpoints=None, ca_cert=None,
                 cert_key=None, cert_cert=None, timeout=None, user=None,
                 password=None):
        self.client = V3Client(endpoints=endpoints, ca_cert=ca_cert,
                               cert_key=cert_key, cert_cert=cert_cert, timeout=timeout, user=user,
                               password=password)
    
    def dispose(self):
        self.client.close()
