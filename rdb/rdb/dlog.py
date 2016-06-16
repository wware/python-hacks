import httplib
import logging
import pprint
import time
import traceback
import urllib
from math import fmod

from rdb import comms

_host_getter = None


def json_record(record):
    return {
        'ipaddr': comms._local_ip,
        'levelname': record.levelname,
        'pathname': record.pathname,
        'lineno': record.lineno,
        'funcName': record.funcName,
        'exc_info': record.exc_info,
        'msg': record.msg,
        'created': record.created
    }


class DistributedHandler(logging.Handler):
    def emit(self, record):
        host_ip = comms.get_host_ip()
        if host_ip is None:
            return
        try:
            params = urllib.urlencode(json_record(record))
            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "Accept": "text/plain"}
            conn = httplib.HTTPConnection(host_ip + ':5000')
            conn.request("POST", "/log", params, headers)
            conn.getresponse()
            conn.close()
        except:
            pass


def extendLogger(logger):
    def _pprint(thing, logger=logger):
        if logger.isEnabledFor(logging.INFO):
            logger._log(logging.INFO, pprint.pformat(thing), [])
    logger.pprint = _pprint

    def _stack(msg=None, logger=logger):
        if logger.isEnabledFor(logging.INFO):
            stuff = traceback.format_stack()[:-1]
            if msg is not None:
                stuff.append(str(msg))
            else:
                stuff[-1] = stuff[-1].rstrip()
            logger._log(logging.INFO, ''.join(stuff), [])
    logger.stack = _stack
