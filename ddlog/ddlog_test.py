from handler import DDHandler
import logging
import datetime

log = logging.getLogger()
ddlog = DDHandler('localhost', 10518, debugging_fields=True, extra_fields=True)
log.addHandler(ddlog)
ddlog.setLevel(logging.DEBUG)
log.setLevel(logging.DEBUG)
log.debug("this is a message at {}".format(datetime.datetime.now()))
try:
    raise ValueError('hi')
except Exception as e:
    log.critical(e, exc_info=True)
