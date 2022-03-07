import logging
import sys
import time

from register import RegSvcClient  # type: ignore

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    endpoints = (("127.0.0.1", 12379), ("127.0.0.1", 22379), ("127.0.0.1", 32379))
    cli = RegSvcClient(endpoints)
    cli.register_service(5, 30, "", "test", "key", "value", logging)

    time.sleep(30)
    cli.stop()
    time.sleep(5)
