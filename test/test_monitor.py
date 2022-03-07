import logging
import sys
import time

from monitor import MonSvcClient  # type: ignore

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


    def func_put(k: str, v: str):
        logging.debug("func_put, need to add kv: %s/%s}", k, v)


    def func_delete(k: str):
        logging.debug("func_delete, need to delete k: %s}", k)


    endpoints = (("127.0.0.1", 12379), ("127.0.0.1", 22379), ("127.0.0.1", 32379))
    cli = MonSvcClient(endpoints)

    cli.monitor_service("", logging, func_put, func_delete)

    time.sleep(100)
    cli.stop()
    time.sleep(5)
