#!/usr/bin/python3
# Copyright (c) 2021, Zsolt KALMAR

import sys
import os
import logging
import time
import signal
import configparser
from mpublisher import AvahiPublisher
import logging
import logging.handlers
import re
import functools



# Read configuration
config = configparser.ConfigParser()
config.read("/etc/mDNS/mDNS.conf")

ttl = config['general']['ttl']
logfile = config['general']['logfile']
loglevel = config['general']['loglevel']

# Initiate logging
logging.basicConfig(filename='/var/log/mDNS.log', level=logging.INFO)
print("Logging started")
cnames = ['gooseberry.local', 'greenberry.local', 'someberry.local', 'fooberry.local']

def handle_signals(publisher, signum, frame):
    """Unpublish all mDNS records and exit cleanly."""

    signame = next(v for v, k in signal.__dict__.items() if k == signum)
    log.info("Exiting on %s...", signame)
    publisher.__del__()

    # Avahi needs time to forget us...
    sleep(1)

    os._exit(0)

def daemonize():
    """Run the process in the background as a daemon."""

    try:
        # First fork to return control to the shell...
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if pid:
        # Quickly terminate the parent process...
        os._exit(0)

    os.setsid()

    try:
        # Second fork to prevent zombies...
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if pid:
        # Quickly terminate the parent process...
        os._exit(0)

    # To make sure we don't block an unmount in the future, in case
    # the current directory resides on a mounted filesystem...
    os.chdir("/")

    # Sanitize permissions...
    os.umask(0o022)

    # Redirect the standard file descriptors to "/dev/null"...
    f = open(os.devnull, "r")
    os.dup2(f.fileno(), sys.stdin.fileno())
    assert sys.stdin.fileno() == 0

    f = open(os.devnull, "r")
    os.dup2(f.fileno(), sys.stdout.fileno())
    assert sys.stdout.fileno() == 1

    f = open(os.devnull, "r")
    os.dup2(f.fileno(), sys.stderr.fileno())
    assert sys.stderr.fileno() == 2

def main():
    daemonize()
    logging.info("mDNS publisher starting...")
    publisher = None
    while True:
        if not publisher or not publisher.available():
            if publisher:
                logging.info("Lost connection with Avahi. Reconnecting...")
            
            publisher = AvahiPublisher(ttl)

            # To make sure records disappear immediately on exit, clean up properly...
            signal.signal(signal.SIGTERM, functools.partial(handle_signals, publisher))
            signal.signal(signal.SIGINT, functools.partial(handle_signals, publisher))
            signal.signal(signal.SIGQUIT, functools.partial(handle_signals, publisher))

            for cname in cnames:
                status = publisher.publish_cname(cname)
                if not status:
                    logging.error("Failed to publish '%s'", cname)
                continue

                if publisher.count() == len(cnames):
                    logging.info("All CNAMEs published")
                else:
                    logging.warning("%d out of %d CNAMEs published", publisher.count(), len(cnames))

        # CNAMEs will exist while this service is kept alive,
        # but we don't actually need to do anything useful...
        sleep(1)


if __name__ == "__main__":
    main()


