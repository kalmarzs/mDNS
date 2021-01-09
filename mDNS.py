#!/usr/bin/python3
# Copyright (c) 2021, Zsolt KALMAR

__all__ = ["main"]

import sys
import os
import signal
import configparser
import logging
import logging.handlers
#import re
import functools
import time

from mpublisher import AvahiPublisher

# Read configuration
config = configparser.ConfigParser()
config.read("/etc/mDNS/mDNS.conf")

ttl = config['general']['ttl']
logfile = config['general']['logfile']
loglevel = config['general']['loglevel']

log = logging.getLogger("mDNS Publisher")


def cnames():
    if config['backend']['backend'] == 'conf':
        cnames = ['gooseberry.local', 'greenberry.local', 'someberry.local', 'fooberry.local']
        return cnames
    #else:
    # DB query
    #reutrn results

def main():
    logging.basicConfig(filename=logfile, logging.DEBUG)
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log.info("mDNS publisher starting...")
    
    publisher = None
    while True:
        if not publisher or not publisher.available():
            if publisher:
                log.info("Lost connection with Avahi. Reconnecting...")
            
            publisher = AvahiPublisher(ttl)
            signal.signal(signal.SIGTERM, functools.partial(handle_signals, publisher))
            signal.signal(signal.SIGINT, functools.partial(handle_signals, publisher))
            signal.signal(signal.SIGQUIT, functools.partial(handle_signals, publisher))

            cnames = cnames()

            for cname in cnames:
                status = publisher.publish_cname(cname, force=False)
                if not status:
                    log.error("Failed to publish '%s'", cname)
                    continue

            if publisher.count() == len(cnames):
                log.info("All CNAMEs published")
            else:
                log.warning("%d out of %d CNAMEs published", publisher.count(), len(cnames))
        
        time.sleep(1)

def handle_signals(publisher, signum, frame):
    """Unpublish all mDNS records and exit cleanly."""

    signame = next(v for v, k in signal.__dict__.items() if k == signum)
    log.info("Exiting on %s...", signame)
    publisher.__del__()

    # Avahi needs time to forget us...
    time.sleep(1)

    os._exit(0)

if __name__ == "__main__":
    main()


