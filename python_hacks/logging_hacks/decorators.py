import linecache
import sys
import time
import trace
import logging
import cProfile
from contextlib import contextmanager
from functools import wraps

from log_frame_caller import logdelta


def trace_to_log(level):
    """
    Example usage::

    @param level: the level at which logging should be done
    @return: a decorator that traces executed Python lines to the root logger
    """
    class Trace(trace.Trace):
        def __init__(self, *args, **kw):
            trace.Trace.__init__(self, *args, **kw)
            self.localtrace = self.localtrace_log

        def globaltrace_lt(self, frame, why, arg):
            if why == 'call':
                filename = frame.f_globals.get('__file__', None)
                if filename:
                    modulename = trace.modname(filename)
                    if modulename is not None:
                        ignore_it = self.ignore.names(filename, modulename)
                        if not ignore_it:
                            return self.localtrace
                else:
                    return None

        def localtrace_log(self, frame, why, arg):
            def log(x):
                logging.getLogger().log(level, x)

            if why == "line":
                filename = frame.f_code.co_filename
                lineno = frame.f_lineno
                with logdelta(1):
                    if self.start_time:
                        log('%.2f' % (time.time() - self.start_time))
                    log(linecache.getline(filename, lineno).rstrip())
            return self.localtrace

    def decorator(f):
        @wraps(f)
        def inner(*args, **kw):
            if logging.getLogger().isEnabledFor(level):
                return Trace().runfunc(f, *args, **kw)
            else:
                return f(*args, **kw)
        return inner
    return decorator


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


if __name__ == '__main__':

    logging.info("\n\n* * * trace_to_log example")

    @trace_to_log(logging.INFO)
    def foo():
        if 5 > 3:
            print 'right'
            x = 3
        else:
            print 'wrong'
            x = 5
        y = 4
        return x + y

    assert foo() == 7

    logging.info("\n\n* * * profile_to_log example")

    def bar():
        with profile_to_log(logging.INFO):
            time.sleep(0.3)

    bar()
