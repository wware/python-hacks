#!/usr/bin/env python

import inspect
import os
import logging
import traceback
from contextlib import contextmanager

_unique = object()

logging.basicConfig(
    format='%(asctime)-15s  %(levelname)s  %(filename)s:%(lineno)d  %(message)s',
    level=logging.INFO
)


def __LINE__():
    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return info.lineno


# pylint: disable=protected-access
def findCaller(_):
    f = logging.currentframe()
    for _ in range(2 + logging._frame_delta):
        if f is not None:
            f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)"
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        if filename == logging._srcfile:
            f = f.f_back
            continue
        rv = (co.co_filename, f.f_lineno, co.co_name)
        break
    return rv
logging.Logger.findCaller = findCaller
logging._frame_delta = 0


@contextmanager
def logdelta(n):
    d = logging._frame_delta
    logging._frame_delta = d + n
    yield
    logging._frame_delta = d
# pylint: enable=protected-access


def ping(msg=_unique):
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        if msg is _unique:
            msg = ""
        else:
            msg = str(msg)
        with logdelta(1):
            logging.debug(msg + '\n' + ''.join(traceback.format_stack()))


def A(x):
    with logdelta(1):
        logging.info('A: ' + x)    # Don't log with this line number


def B(x):
    with logdelta(2):
        logging.info('B: ' + x)    # or with this line number


def C(x):
    B(x)                           # or this line number

A('hello')                         # Instead, log with THIS line number
C('hello')                         # or THIS line number
