#!/usr/bin/env python3

import ddlog
import logging
import socket

log = logging.getLogger()
ddlog = ddlog.DDHandler('localhost', 10516, debugging_fields=True, extra_fields=True)
log.addHandler(ddlog)

big = "A"*70000
log.error(big)
