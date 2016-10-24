#!/usr/bin/env python

from contextlib import contextmanager
import argparse
import inspect
import logging
import pdb
import re
import pprint
import subprocess
import sys
import tempfile
from functools import wraps, partial


logging.basicConfig(
    format='%(asctime)-15s  %(levelname)s  %(filename)s:%(lineno)d  %(message)s'
)

_debug_magic = False
_enter_leave_indent = 0


def _pprint(thing, logger=logging.getLogger()):
    if logger.isEnabledFor(logging.INFO):
        logger._log(logging.INFO, '\n' + pprint.pformat(thing), [])
logging.getLogger().pprint = _pprint


def dig(obj, n):
    if (obj is None or
            isinstance(obj, int) or
            isinstance(obj, float) or
            isinstance(obj, complex) or
            isinstance(obj, str) or
            isinstance(obj, unicode) or
            isinstance(obj, bool)):
        return obj
    if n == 0:
        return "..."
    if isinstance(obj, list):
        iterable = range(len(obj))

        def selector(k, obj=obj):
            return obj[k]

        def keyfunc(x):
            return 'list-{0}'.format(x)
    elif isinstance(obj, tuple):
        iterable = range(len(obj))

        def selector(k, obj=obj):
            return obj[k]

        def keyfunc(x):
            return 'tuple-{0}'.format(x)
    elif isinstance(obj, set):
        obj = list(obj)
        iterable = range(len(obj))

        def selector(k, obj=obj):
            return obj[k]

        def keyfunc(x):
            return 'set-{0}'.format(x)
    elif isinstance(obj, dict):
        iterable = [k for k in obj.keys() if not k.startswith('__')]

        def selector(k, obj=obj):
            return obj.get(k)

        def keyfunc(x):
            return x
    else:
        iterable = [k for k in dir(obj) if not k.startswith('__')]

        def selector(k, obj=obj):
            return getattr(obj, k)

        def keyfunc(x):
            return '.' + x

    dct = {}
    for k in iterable:
        y = selector(k)
        try:
            dct[keyfunc(k)] = dig(y, n - 1)
        except:
            pass
    return dct


def stderr_on_exception(*args):
    with tempfile.NamedTemporaryFile() as f:
        try:
            subprocess.check_call(args, stderr=f)
        except Exception as e:
            if _debug_magic:
                f.seek(0)
                logging.error(f.read())
            logging.exception(e)


def enter_leave(args=True, method=False):
    def decorator(f):
        n = 4
        fmt = logging.Formatter(
            '%(asctime)-15s  %(levelname)s  {0}:{1}  %(message)s'.format(
                re.sub('^\./', '', f.func_code.co_filename),
                f.func_code.co_firstlineno + 1
            )
        )

        @wraps(f)
        def inner(*args, **kw):
            global _enter_leave_indent
            if not _debug_magic:
                return f(*args, **kw)
            oldformats = [h.formatter for h in logging.root.handlers]
            for h in logging.root.handlers:
                h.formatter = fmt
            indent = (n * _enter_leave_indent) * " "
            if args:
                display_args = method and args[1:] or args
                logging.debug('{0}Entering {1}(*{2}, **{3})'.format(
                    indent, f.func_name, display_args, kw
                ))
            else:
                logging.debug('{0}Entering {1}'.format(indent, f.func_name))
            _enter_leave_indent += 1
            try:
                r = f(*args, **kw)
                _enter_leave_indent -= 1
                indent = (n * _enter_leave_indent) * " "
                if args:
                    logging.debug('{0}Leaving {1} -> {2}'.format(indent, f.func_name, r))
                else:
                    logging.debug('{0}Leaving {1}'.format(indent, f.func_name))
                return r
            except Exception as e:
                _enter_leave_indent -= 1
                logging.exception(e)
                raise e
            finally:
                for h, old in zip(logging.root.handlers, oldformats):
                    h.formatter = old
        return inner
    return decorator


def set_debug_magic():
    global _debug_magic
    _debug_magic = True
    logging.getLogger().setLevel(logging.DEBUG)


@enter_leave()
def add(x, y):
    return x + y


@enter_leave()
def multiply(x, y):
    sum = 0
    for i in range(x):
        sum = add(y, sum)
    return sum


def get_stack():
    def frame2dict(frame):
        info = inspect.getframeinfo(frame[0])
        return {
            'locals': frame[0].f_locals,
            'file': info.filename,
            'function': info.function,
            'line': info.lineno
        }
    stuff = [frame2dict(frame) for frame in inspect.stack()[1:]]
    if _debug_magic:
        logging.getLogger().pprint(stuff)
    return stuff


thingsToTry = range(3)

parser = argparse.ArgumentParser(
    prog=sys.argv[0],
    description='Random hacks'
)
parser.add_argument('--debug',
    action='store_true',
    help='enable debugging output',
)
parser.add_argument('--pdb',
    action='store_true',
    help='run with PDB',
)
thing_choices = ['alpha', 'bravo', 'charlie', 'delta']
parser.add_argument('--things',
    nargs='+',
    choices=thing_choices,
    help='which tests to run',
)

options = parser.parse_args(sys.argv[1:])
if options.debug:
    set_debug_magic()
if options.pdb:
    pdb.set_trace()
if options.things is None:
    options.things = thing_choices


if 'alpha' in options.things:
    stderr_on_exception('ls', 'q*')


if 'bravo' in options.things:
    logging.getLogger().info(multiply(3, 4))


if 'charlie' in options.things:
    def called():
        logging.getLogger().pprint(get_stack())

    def main():
        called()

    main()


if 'delta' in options.things:
    @enter_leave(args=False)
    def add2(x, y):
        return x + y + add(x, y)

    class Foo(object):
        @enter_leave(method=True)
        def bar(self, *args):
            assert isinstance(self, Foo), self
            return args[:1]

    set_debug_magic()
    logging.debug('Start')
    add(3, 4)
    add2(6, 8)

    f = Foo()
    f.bar(1, 2, 3)
    logging.debug('Finish')
