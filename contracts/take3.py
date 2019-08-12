"""
Take yet another stab at DbC for Python, addressing the following issues.
(1) Preconditions should not apply to each argument separately.
(2) Postconditions should be able to look at return value and also args and kwargs.
(3) Don't forget class invariants.
"""

import pdb
import argparse
import types
import inspect
import logging
import pprint
from functools import wraps
from contextlib import contextmanager


class ContractViolation(Exception): pass
class PreconditionViolation(ContractViolation): pass
class PostconditionViolation(ContractViolation): pass
class InvariantViolation(ContractViolation): pass


class ContractClass(object):
    @classmethod
    def apply(cls, target):
        contract = cls()
        if isinstance(target, types.TypeType):
            return contract._apply_class(target)
        else:
            return contract._apply_function(target)

    def _nullfunc(self, *args, **kw):
        return True

    def _apply_function(self, target):
        pre = getattr(self, 'pre_' + target.__name__, None)
        post = getattr(self, 'post_' + target.__name__, None)
        if pre is None:
            pre = self._nullfunc
        if post is None:
            post = self._nullfunc
        if pre is self._nullfunc and post is self._nullfunc:
            return target
        this = self

        @wraps(target)
        def inner(*args, **kwargs):
            m_args = args
            if isinstance(target, types.MethodType):
                m_args = args[1:]
                if not this.invariant(args[0]):
                    raise InvariantViolation(target)
            if not pre(*m_args, **kwargs):
                raise PreconditionViolation(target)
            retval = target(*args, **kwargs)
            if isinstance(target, types.MethodType):
                if not this.invariant(args[0]):
                    raise InvariantViolation(target)
            if not post(retval, *m_args, **kwargs):
                raise PostconditionViolation(target)
            return retval

        return inner

    def _apply_class(self, target):
        for method in [
            getattr(target, m) for m in dir(target)
            if not m.startswith("_") and
                    isinstance(getattr(target, m), types.MethodType)
        ]:
            setattr(target, method.__name__, self._apply_function(method))
        return target


################################################


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


bad_return_value = False

@contextmanager
def misbehave():
    global bad_return_value
    try:
        bad_return_value = True
        yield
    finally:
        bad_return_value = False

@contextmanager
def expect_failure():
    try:
        yield
        raise ContractViolation("there was supposed to be a failure here")
    except ContractViolation:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
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
        if bad_return_value:
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
    if bad_return_value:
        return 19
    else:
        return 'some return value'


quux(1, 0)

with expect_failure():
    quux(1, 2)


with expect_failure():
    with misbehave():
        quux(0.3, 0.5)

print 'OK'
