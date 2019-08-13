"""
Take yet another stab at DbC for Python, addressing the following issues.
(1) Preconditions should not apply to each argument separately.
(2) Postconditions should be able to look at return value and also
    args and kwargs.
(3) Don't forget class invariants.
"""

import types
from functools import wraps


class ContractViolation(Exception):
    pass


class PreconditionViolation(ContractViolation):
    pass


class PostconditionViolation(ContractViolation):
    pass


class InvariantViolation(ContractViolation):
    pass


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

        def fmt(*args):
            nope = object()
            retval = nope
            if len(args) == 4:
                fn, retval, args, kwargs = args
            else:
                fn, args, kwargs = args
            fname = fn.__name__
            if args and hasattr(args[0], "__dict__"):
                c, args = args[0], args[1:]
                fname = c.__class__.__name__ + "()." + fname
            s = fname + "(" + ", ".join(map(str, args))
            if kwargs:
                s += ", " + ", ".join([k + "=" +  str(v) for k, v in kwargs.items()])
            s += ")"
            if retval is not nope:
                s += " ==> " + str(retval)
            return "\n    " + s + "\n"

        @wraps(target)
        def inner(*args, **kwargs):
            m_args = args
            if isinstance(target, types.MethodType):
                m_args = args[1:]
                if not this.invariant(args[0]):
                    raise InvariantViolation(fmt(target, args, kwargs))
            if not pre(*m_args, **kwargs):
                raise PreconditionViolation(fmt(target, args, kwargs))
            retval = target(*args, **kwargs)
            if isinstance(target, types.MethodType):
                if not this.invariant(args[0]):
                    raise InvariantViolation(fmt(target, args, kwargs))
            if not post(retval, *m_args, **kwargs):
                raise PostconditionViolation(fmt(target, retval, args, kwargs))
            return retval

        return inner

    def _apply_class(self, target):
        for method in [
            getattr(target, m) for m in dir(target)
            if not m.startswith("_") and
            isinstance(getattr(target, m), types.MethodType)
        ]:
            setattr(target, method.__name__,
                    self._apply_function(method))
        return target
