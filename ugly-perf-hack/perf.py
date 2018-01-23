#!/usr/bin/env python

"""
An ill-designed performance measuring thing for Python, use at your own risk.
I'd prefer line_profiler except I'm on Python 2.7 and cannot upgrade.
"""

import logging
import timeit
import traceback
from functools import wraps
from contextlib import contextmanager
from collections import Counter

_WIDTH = 50


class ProfilerHack(object):
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
            yield None
            end = timeit.default_timer()
            self._profile_info[end] = (name, end - start)
        else:
            yield None

########################

logFormatter = logging.Formatter(
    "%(asctime)-15s  %(levelname)s  %(filename)s:%(lineno)d  %(message)s"
)
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.setLevel(logging.DEBUG)

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
