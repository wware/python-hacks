import os
import inspect
import sys
from functools import wraps
from contextlib import contextmanager
import logging
from typing import Dict

logging.basicConfig(
    format='%(filename)s:%(lineno)d  ' +
           '%(message)s',
    level=logging.INFO
)

"""
Forget pickle. Let's build a data structure out of 4 byte integers using a fast lookup.
A four-element type contains a filename index, a line number, a function name index,
and an index for a dict of local variables. The dict maps indices to indices where the
values are repr strings. The log is a directory of binary files containing these things
in order, plus the lookup stuff. The files are fairly small, 16k to 32k each, so they
can be pulled efficiently into buffers and traversed quickly. The debugger is presented
as a web app running on the machine where the code ran originally so all the source
files are available.

This can be so efficient that's you don't need to worry about deltas. The trick here
will be making the lips lightning fast. Do that right and you'll have minimal performance
impact while collecting.
"""

_already = set()
unique = object()
indices: Dict[int, str] = {}
r_indices: Dict[str, int] = {}
source_files = {}


def get_source_file(fname):
    fname = os.path.realpath(fname)
    if fname not in source_files:
        source_files[fname] = open(fname, 'r').readlines()
    return source_files[fname]


def index(s: str):
    n = r_indices.get(s, unique)
    if n is unique:
        n = len(r_indices)
        r_indices[s] = n
        indices[n] = s
    return n


def get_tuple(frame) -> tuple:
    co = frame.f_code
    _file = os.path.realpath(co.co_filename)
    _func = co.co_name
    return (index(_file), frame.f_lineno, index(_func))


def apply_diags():
    frame = inspect.currentframe().f_back
    co = frame.f_code
    _file = os.path.realpath(co.co_filename)

    def trace_lines(frame, event, arg):
        logging.info(event)
        if event == 'line':
            t = get_tuple(frame)
            fi = indices[t[0]]
            fu = indices[t[2]]
            these_lines = get_source_file(fi)
            logging.info((fi, t[1], fu, these_lines[t[1] - 1]))

    def setter(frame, event, arg):
        logging.info(event)
        return trace_lines

    def decorator(f):
        @wraps(f)
        def inner(*args, **kw):
            orig = sys.gettrace()
            try:
                sys.settrace(setter)
                return f(*args, **kw)
            finally:
                sys.settrace(orig)
        return inner
    return decorator


@apply_diags()
def first_function(x, y, z):
    x = x ** 2
    y = second_function(y, z)
    return x + y


def second_function(y, z):
    y = y ** 2
    y += z ** 2
    return y


print(first_function(1, 2, 3))
