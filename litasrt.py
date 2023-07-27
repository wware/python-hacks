"""
More detailed explanatory asserts can help to clarify code and provide
a narrative about what's going on, what is intended or expected, etc.
So a message might look like this.

    Notify {name} that the errno is {errno}.
    and object attributes are
    foo.a = {foo.a}
    foo.b = {foo.b}

Let's accommodate pre-conditions and post-conditions in a sort of a
design-by-contract way. Formatting allows us to include variables. Long
detailed strings like this can form a saga that explains the intent of
the code, what is known with certainty, what questions remain open,
what actions still need to be taken. The conditions can test whatever
you need for the code to be successful.

Wouldn't it be fun if we could do something with Markdown in these
long strings? Maybe a project for another time. But boy would some
LaTeX equations be impressive right about here...
"""

import inspect
import pprint
import string
import os
import sys
from functools import wraps
from contextlib import contextmanager

# when we don't actually want an exception raised
MESSAGE_ONLY = object()


class BlankFormatter(string.Formatter):
    def __init__(self, default='???'):
        self.default=default

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default)
        else:
            return string.Formatter.get_value(key, args, kwds)


fmt = BlankFormatter()


def getvars(n=0, **other):
    frame = inspect.currentframe()
    for _ in range(n + 1):
        frame = frame and frame.f_back
    if frame is None:
        return {}
    d = frame.f_globals.copy()
    d.update(frame.f_locals)
    d.update(other)
    return d


####################################################
# APPROACH 1.
# Define a function where calling the function is like
# an assert statement.

def literate_assert(template):
    # https://stackoverflow.com/questions/42497625, 2nd answer
    def check(cond, **kwargs):
        if cond is MESSAGE_ONLY or not cond:
            d = getvars(1, **kwargs)
            s = fmt.format(template, **d)
            if cond is MESSAGE_ONLY:
                print(s)
            else:
                raise AssertionError(s)
    return check


###################
# APPROACH 2.
# Define a decorator that applies pre-conditions and post-conditions
# to a function, ala DbC style programming.


def dbc_func(msg, pre=None, post=None):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kw):
            if pre is not None:
                d = getvars(1, **kw)
                d.update(dict(zip(f.__code__.co_varnames, args)))
                assert pre(*args, **kw), fmt.format(msg, **d)
            R = f(*args, **kw)
            if post is not None:
                d = getvars(1, R=R, **kw)
                d.update(dict(zip(f.__code__.co_varnames, args)))
                assert post(*args + (R,), **kw), fmt.format(msg, **d)
            return R
        return inner
    return decorator


###############################
# APPROACH 3.
# Define a context manager that applies DbC-style conditions
# to a code block inside a function.


@contextmanager
def dbc_block(msg, pre=None, post=None):
    assert pre is None or pre(), fmt.format(msg, **getvars(2))
    yield
    assert post is None or post(), fmt.format(msg, **getvars(2))


if __name__ == '__main__':
    # test all these things, show example usages

    ####################################################
    # APPROACH 1.

    A = literate_assert(__doc__)
    # Assign variables after defining the assert above. We want to
    # make sure we didn't accidentally bake in permanent values for
    # the variables: we want formatting to work correctly.
    class Foo(object):
        pass

    foo = Foo()
    foo.a = 123
    foo.b = 456
    name = "wware"
    errno = 31415926

    precondition_failed = (os.getenv("OUCH0", "") != "")
    A(not precondition_failed)
    print("Do some exciting functional code stuff")
    postcondition_failed = (os.getenv("OUCH1", "") != "")
    A(not postcondition_failed, errno=12345)

    ###################
    # APPROACH 2.

    @dbc_func(
        __doc__,
        pre=lambda a, b, c: isinstance(a, int),
        post=lambda a, b, c, R: R == a + 3
    )
    def myfunction(a, b, c):
        return a + 3

    print(myfunction(11, "def", "ghi"))
    if os.getenv("OUCH2", "") != "":
        # fail because "abc" is not an integer
        # so the precondition fails
        print(myfunction("abc", "def", "ghi"))

    ###############################
    # APPROACH 3.

    def foo():
        a = 3
        if os.getenv("OUCH3", "") != "":
            a = 11
        with dbc_block(
            """Fret about {a}, which should be 3, and {b} which should be 4""",
            pre=lambda: a == 3,
            post=lambda: b == 4
        ):
            b = a + 1
            if os.getenv("OUCH4", "") != "":
                b = a + 2
        return (a, b)


    print(foo())
