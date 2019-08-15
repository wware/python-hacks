"""
Take yet another stab at DbC for Python, addressing the following issues.
(1) Preconditions should not apply to each argument separately.
(2) Postconditions should be able to look at return value and also
    args and kwargs.
(3) Don't forget class invariants.
"""

import argparse
import logging
from wwc import ContractClass, ContractViolation
from contextlib import contextmanager

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='turn on debug-level logging',
)
opts = parser.parse_args()
if opts.debug:
    logging.getLogger().setLevel(logging.DEBUG)


################################################


_bad_return_value = False


@contextmanager
def misbehave():
    global _bad_return_value
    try:
        _bad_return_value = True
        yield
    finally:
        _bad_return_value = False


@contextmanager
def expect_failure():
    try:
        yield
        raise Exception("there was supposed to be a failure here")
    except ContractViolation as cv:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            # logging.error(cv)
            logging.exception("Expected failure - this is OK")


################################################


class FooContract(ContractClass):
    def invariant(self, target):
        return target.z == 'Zyxxy'

    def pre_foo(self, x, y):
        return x * x + y * y < 1.000000001

    def post_foo(self, retval, x, y):
        return isinstance(retval, str)


@FooContract.apply
class FooClass(object):
    def __init__(self):
        self.z = 'Zyxxy'

    def foo(self, x, y):
        if _bad_return_value:
            return 19
        else:
            return 'some return value'


f = FooClass()
f.foo(0.3, 0.5)

with expect_failure():
    f.foo(12, 14)

with expect_failure():
    with misbehave():
        f.foo(0.3, 0.5)


################################################


class QuuxContract(ContractClass):
    def pre_quux(self, x, y):
        return x * x + y * y < 1.000000001

    def post_quux(self, retval, x, y):
        return isinstance(retval, str)


@QuuxContract.apply
def quux(x, y):
    if _bad_return_value:
        return 19
    else:
        return 'some return value'


quux(1, 0)

with expect_failure():
    quux(1, 2)


with expect_failure():
    with misbehave():
        quux(0.3, 0.5)

print('OK')



#################################################

from functools import wraps


def pre(expr):
    def decorator(fn):
        fc = fn.func_code
        argnames = fc.co_varnames[:fc.co_argcount]
        @wraps(fn)
        def inner(*args, **kw):
            vars = dict(zip(argnames, args))
            vars.update(kw)
            assert eval(expr, vars.copy()), "\nPrecondition failed: {0}\n{1}".format(
                expr,
                ", ".join(["{0} = {1}".format(k, v) for k, v in vars.items()])
            )
            return fn(*args, **kw)
        return inner
    return decorator


def post(expr):
    def decorator(fn):
        fc = fn.func_code
        argnames = fc.co_varnames[:fc.co_argcount]
        @wraps(fn)
        def inner(*args, **kw):
            vars = dict(zip(argnames, args))
            vars.update(kw)
            vars['retval'] = retval = fn(*args, **kw)
            assert eval(expr, vars.copy()), "\nPostcondition failed: {0}\n{1}".format(
                expr,
                ", ".join(["{0} = {1}".format(k, v) for k, v in vars.items()])
            )
            return retval
        return inner
    return decorator


@pre("x * x + y * y < 1.000000001")
@post("isinstance(retval, str)")
def quux(x, y):
    if _bad_return_value:
        return 19
    else:
        return 'some return value'


quux(1, 0)

with expect_failure():
    quux(1, 2)


with expect_failure():
    with misbehave():
        quux(0.3, 0.5)
