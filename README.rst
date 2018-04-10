DDLog
-----

This program will send log data to a local datadog-agent.  To use it, create a handler to your logger:

    >>> import ddlog
    >>> import logging
    >>>
    >>> log = logging.getLogger()
    >>> ddlog = ddlog.handler('localhost', 10516, compress=False, debugging_fields=True, level_names=True, extra_fields=True)
    >>> log.addHandler(ddlog)
