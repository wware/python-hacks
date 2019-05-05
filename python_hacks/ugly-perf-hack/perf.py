#!/usr/bin/env python

import logging
import os
import sys
import timeit
import traceback
import cProfile
from functools import wraps
from contextlib import contextmanager
from collections import Counter

logging.basicConfig(
    format='%(asctime)-15s  %(levelname)s  %(filename)s:%(lineno)d  %(message)s',
    level=logging.DEBUG
    # level=logging.INFO
)

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


_WIDTH = 50

class ProfilerHack(object):
    """
    An ill-designed performance measuring thing for Python, use at your own risk.
    I'd prefer line_profiler except I'm on Python 2.7 and cannot upgrade.
    """
    _profilers = {}

    @classmethod
    def get(cls, name=None):
        if name not in cls._profilers:
            cls._profilers[name] = cls()
        return cls._profilers[name]

    def __init__(self):
        self._profile_info = {}

    def pretty_name(self, file, line, msg):
        r = "{0}({1}) {2}".format(file, line, msg)
        if len(r) > _WIDTH:
            r = "..." + r[-(_WIDTH-3):]
        return r

    def profile(self, f):
        name = self.pretty_name(
            f.func_code.co_filename,
            f.func_code.co_firstlineno,
            f.func_code.co_name
        )

        @wraps(f)
        def wrapper_with_debug(*args, **kwargs):
            start = timeit.default_timer()
            r = f(*args, **kwargs)
            end = timeit.default_timer()
            self._profile_info[end] = (name, end - start)
            return r
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            return wrapper_with_debug
        else:
            return f

    def get_profile(self):
        d = {}
        for (_, (name, t)) in self._profile_info.items():
            if name not in d:
                d[name] = 0.
            d[name] += t
        return d

    def show_profile(self):
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            with logdelta(1):
                lst = [(-t, name) for name, t in self.get_profile().items()]
                lst.sort()
                for t, name in lst:
                    fmt = "{0:>" + str(_WIDTH) + "} {1}"
                    logging.debug(fmt.format(name, -t))

    @contextmanager
    def context(self, legend):
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            filename, line, _, _ = traceback.extract_stack()[-3]
            name = self.pretty_name(filename, line, legend)
            start = timeit.default_timer()
            yield
            end = timeit.default_timer()
            self._profile_info[end] = (name, end - start)
        else:
            yield

if False:
    ## Let's test it

    p = ProfilerHack.get()
    c = Counter()


    @p.profile
    def inner():
        with p.context('inner update loop'):
            for _ in range(100):
                c.update('abcd')


    @p.profile
    def middle():
        for _ in range(100):
            for _ in range(100):
                c.update('efgh')
            inner()


    @p.profile
    def outer():
        for _ in range(100):
            with p.context('outer update loop'):
                for _ in range(100):
                    c.update('ijkl')
            middle()

    outer()

    p.show_profile()

########################

@contextmanager
def profile_to_log(log_level):
    class StreamToLogger(object):
        def __init__(self, logger):
            self.logger = logger
            self.linebuf = ''

        def write(self, buf):
            if buf.endswith("\n"):
                self.logger.log(log_level, self.linebuf + buf.rstrip())
                self.linebuf = ''
            else:
                self.linebuf += buf

        def flush(self):
            pass

    logger = logging.getLogger()
    pr = None
    enabled = logger.isEnabledFor(log_level)
    try:
        if enabled:
            pr = cProfile.Profile()
            pr.enable()
        yield
    finally:
        if enabled and pr is not None:
            pr.disable()
            orig_ss, sys.stdout = sys.stdout, StreamToLogger(logger)
            pr.print_stats(sort='tottime')
            sys.stdout = orig_ss

########################

c = Counter()
n = 50


def inner():
    for _ in range(n):
        c.update('abcd')


def middle():
    for _ in range(n):
        for _ in range(n):
            c.update('efgh')
        inner()


def outer():
    for _ in range(n):
        for _ in range(n):
            c.update('ijkl')
        middle()

with profile_to_log(logging.INFO):
    outer()
