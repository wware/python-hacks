import os
import sys
import inspect
import linecache
import logging
from functools import wraps


_unassigned = object()
level = logging.DEBUG
logger = logging.getLogger()
h = logging.StreamHandler(sys.stderr)
h.setFormatter(logging.Formatter("%(message)s"))
logger.setLevel(level)
h.setLevel(level)
logger.handlers = [h]
logger.propagate = False


class Watcher(object):
    def __init__(self, vblname):
        self._vblname = vblname
        self._value = _unassigned

    def check(self, frameInfo):
        old, new = self._value, frameInfo.locals.get(self._vblname, _unassigned)
        if old != new:
            if new is _unassigned:
                logger.debug(f"{self._vblname} has gone out of scope")
            elif old is _unassigned:
                logger.debug(f"{self._vblname} has come into scope, value is {new}")
            else:
                logger.debug(f"{self._vblname} has changed value to {new}")
            self._value = new


class FrameInfo(object):
    def __init__(self, frame):
        self._frame = frame
        co = frame.f_code
        self._line_no = frame.f_lineno
        self._func = co.co_name
        self._file = os.path.realpath(co.co_filename)

    def to_str(self):
        return f"{self.file}:{self.line_no} {self.line}"

    @property
    def frame(self):
        return self._line

    @property
    def locals(self):
        return self._frame.f_locals

    @property
    def line(self):
        return linecache.getline(self._file, self._line_no).rstrip()

    @property
    def line_no(self):
        return self._line_no

    @property
    def file(self):
        return self._file

    @property
    def func(self):
        return self._func


this_file = [None]

def default_qualifier(_file, _func):
    _file = os.path.realpath(_file)
    return _file == this_file[0]


def apply_diags(target=None, qual=None, hook=None):
    if qual is None:
        def _qual(*_):
            return True
        qual = _qual
    elif isinstance(qual, bool):
        qual = _qual

    def trace_lines(frame, event, _):
        if event == 'line':
            co = frame.f_code
            _func = co.co_name
            _file = os.path.realpath(co.co_filename)
            if qual(_file, _func):
                hook(FrameInfo(frame))

    def decorator(f):
        @wraps(f)
        def inner(*args, **kw):
            orig = sys.gettrace()
            try:
                sys.settrace(
                    lambda frame, event, arg:
                    trace_lines if event == 'call' else None
                )
                return f(*args, **kw)
            finally:
                sys.settrace(orig)
        return inner

    target = target or 'main'
    _here = inspect.currentframe().f_back.f_back
    this_file[0] = _here.f_code.co_filename
    _locals = _here.f_locals
    _locals[target] = decorator(_locals[target])


w = Watcher(vblname='i')


def hook(frame):
    logger.debug(frame.to_str())


def hook1(frame):
    logger.debug(frame.locals)


def hook2(frame):
    w.check(frame)


def main():
    # apply_diags(target='main', hook=hook)
    apply_diags(target='main', hook=hook2)
