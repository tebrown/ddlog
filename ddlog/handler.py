import datetime
import sys
import logging
import json
import traceback
import socket
from logging.handlers import DatagramHandler

PY3 = sys.version_info[0] == 3

if PY3:
    data, text = bytes, str
else:
    data, text = str, unicode

def _canSendUDPPacketOfSize(sock, packetSize):
   ip_address = "127.0.0.1"
   port = 5005
   try:
      msg = b"A" * packetSize
      if (sock.sendto(msg, (ip_address, port)) == len(msg)):
         return True
   except:
      pass
   return False

def _get_max_udp_packet_size_aux(sock, largestKnownGoodSize, smallestKnownBadSize):
   if ((largestKnownGoodSize+1) == smallestKnownBadSize):
      return largestKnownGoodSize
   else:
      newMidSize = int((largestKnownGoodSize+smallestKnownBadSize)/2)
      if (_canSendUDPPacketOfSize(sock, newMidSize)):
         return _get_max_udp_packet_size_aux(sock, newMidSize, smallestKnownBadSize)
      else:
         return _get_max_udp_packet_size_aux(sock, largestKnownGoodSize, newMidSize)

def _get_max_udp_packet_size():
   sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   ret = _get_max_udp_packet_size_aux(sock, 0, 65508)
   sock.close()
   return ret or 8192-48  # 48 bytes ethernet header



class DDHandler(DatagramHandler):
    """Graylog Extended Log Format handler

    :param host: The host of the graylog server.
    :param port: The port of the graylog server (default 12201).
    :param debugging_fields: Send debug fields if true (the default).
    :param extra_fields: Send extra fields on the log record to graylog
        if true (the default).
    :param fqdn: Use fully qualified domain name of localhost as source
        host (socket.getfqdn()).
    :param localname: Use specified hostname as source host.
    :param facility: Replace facility with specified value. If specified,
        record.name will be passed as `logger` parameter.
    :par
        of numerical values. Defaults to False
    """

    def __init__(self, host, port=10518,
                 debugging_fields=True, extra_fields=True, fqdn=False,
                 localname=None, facility=None):
        self.debugging_fields = debugging_fields
        self.extra_fields = extra_fields
        self.fqdn = fqdn
        self.localname = localname
        self.facility = facility
        self._max_pkt_size = _get_max_udp_packet_size()
        DatagramHandler.__init__(self, host, port)

    def send(self, s):
        try:
            DatagramHandler.send(self, s)
        except OSError:
            try:
                DatagramHandler.send(self, s[:self._max_pkt_size-3]+b"...")
            except OSError:
                DatagramHandler.send(self, s[:1021]+b"...")
            

    def makePickle(self, record):
        message_dict = make_message_dict(
            record, self.debugging_fields, self.extra_fields, self.fqdn,
            self.localname, self.facility)
        packed = message_to_json(message_dict)
        return packed



def make_message_dict(record, debugging_fields, extra_fields, fqdn, localname, facility=None):
    if fqdn:
        host = socket.getfqdn()
    elif localname:
        host = localname
    else:
        host = socket.gethostname()
    fields = {'version': "1.0",
              'host': host,
              'message': record.getMessage(),
              }

    if debugging_fields:
        fields.update({
              'args': record.args,
              'created': record.created,
              'filename': record.filename,
              'funcName': record.funcName,
              'levelname': record.levelname,
              'logger.name': record.name,
              'lineno': record.lineno,
              'module': record.module,
              'msecs': record.msecs,
              'name': record.name,
              'pathname': record.pathname,
              'pid': record.process,
              'processName': record.processName,
              'relativeCreated': record.relativeCreated,
              'logger.tid': record.thread,
              'logger.thread_name': record.threadName
        })

    if facility:
        fields['facility'] = facility

    if record.exc_info:
        fields.update({
            'error.message': str(record.exc_info[1]),
            'error.stack': '\n'.join(traceback.format_exception(*record.exc_info)),
            'error.kind': str(record.exc_info[0])
        })

    if extra_fields:
        fields = add_extra_fields(fields, record)
    return fields

SYSLOG_LEVELS = {
    logging.CRITICAL: 2,
    logging.ERROR: 3,
    logging.WARNING: 4,
    logging.INFO: 6,
    logging.DEBUG: 7,
}


def add_extra_fields(message_dict, record):
    # skip_list is used to filter additional fields in a log message.
    # It contains all attributes listed in
    # http://docs.python.org/library/logging.html#logrecord-attributes
    # plus exc_text, which is only found in the logging module source,
    # and id, which is prohibited by the GELF format.
    skip_list = (
        'args', 'asctime', 'created', 'exc_info',  'exc_text', 'filename',
        'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
        'msecs', 'message', 'msg', 'name', 'pathname', 'process',
        'processName', 'relativeCreated', 'thread', 'threadName')

    for key, value in record.__dict__.items():
        if key not in skip_list and not key.startswith('_'):
            message_dict['%s' % key] = value
    return message_dict


def smarter_repr(obj):
    """ convert JSON incompatible object to string"""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    return repr(obj)


def message_to_json(obj):
    """ convert object to a JSON-encoded string"""
    obj = sanitize(obj)
    serialized = json.dumps(obj)
    serialized += "\n\r"
    return serialized.encode('utf-8')


def sanitize(obj):
    """ convert all strings records of the object to unicode """
    if isinstance(obj, dict):
        return dict((sanitize(k), sanitize(v)) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return obj.__class__([sanitize(i) for i in obj])
    if isinstance(obj, data):
        obj = obj.decode('utf-8', errors='replace')
    return obj
