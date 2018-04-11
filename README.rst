DDLog
-----

This program will send log data to a local datadog-agent.  To use it, create a handler to your logger:

    >>> import ddlog
    >>> import logging
    >>>
    >>> log = logging.getLogger()
    >>> ddlog = ddlog.DDHandler('localhost', 10516, debugging_fields=True, extra_fields=True)
    >>> log.addHandler(ddlog)
