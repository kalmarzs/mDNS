#!/usr/bin/python3
# Copyright (c) 2021, Zsolt KALMAR

import sys
import os
import logging
import syslog
import signal

# The publisher needs to be initialized in the loop, to handle disconnects...
    publisher = None

    while True:
        if not publisher or not publisher.available():
            if publisher:
                log.info("Lost connection with Avahi. Reconnecting...")

            publisher = AvahiPublisher(60)

            # To make sure records disappear immediately on exit, clean up properly...
            signal.signal(signal.SIGTERM, functools.partial(handle_signals, publisher))
            signal.signal(signal.SIGINT, functools.partial(handle_signals, publisher))
            signal.signal(signal.SIGQUIT, functools.partial(handle_signals, publisher))

            for cname in args.cnames:
                status = publisher.publish_cname(cname, args.force)
                if not status:
                    log.error("Failed to publish '%s'", cname)
                    continue

            if publisher.count() == len(args.cnames):
                log.info("All CNAMEs published")
            else:
                log.warning("%d out of %d CNAMEs published", publisher.count(), len(args.cnames))

        # CNAMEs will exist while this service is kept alive,
        # but we don't actually need to do anything useful...
        sleep(1)


if __name__ == "__main__":
    command.main()


