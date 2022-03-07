#!/usr/bin/env python
# encoding: utf-8

from etcd3.client import MultiEndpointEtcd3Client, Endpoint  # type: ignore


class V3Client(MultiEndpointEtcd3Client):
    def __init__(self, end_points=None, ca_cert=None,
                 cert_key=None, cert_cert=None, timeout=None, user=None,
                 password=None, grpc_options=None):
        
        # Step 1: verify credentials
        cert_params = [c is not None for c in (cert_cert, cert_key)]
        if ca_cert is not None:
            if all(cert_params):
                credentials = self.get_secure_creds(
                    ca_cert,
                    cert_key,
                    cert_cert
                )
                self.uses_secure_channel = True
            elif any(cert_params):
                # some of the cert parameters are set
                raise ValueError(
                    'to use a secure channel ca_cert is required by itself, '
                    'or cert_cert and cert_key must both be specified.')
            else:
                credentials = self.get_secure_creds(ca_cert, None, None)
                self.uses_secure_channel = True
        else:
            self.uses_secure_channel = False
            credentials = None
        
        # Step 2: create Endpoint
        assert (end_points is not None)
        eps_cred = []
        for ep in end_points:
            assert (len(ep) == 2)
            ep_cred = Endpoint(ep[0], ep[1], secure=self.uses_secure_channel,
                               creds=credentials, opts=grpc_options)
            eps_cred.append(ep_cred)
        
        super(V3Client, self).__init__(endpoints=eps_cred, timeout=timeout,
                                       user=user, password=password)
