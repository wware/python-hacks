import argparse
import logging
import inspect
import pprint
from contextlib import contextmanager
from functools import wraps


parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    action='store_true',
    help='turn on debug-level logging',
)
parser.add_argument(
    '-f', '--force',
    action='store_true',
    help='force failures, do not forgive them',
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
    except:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.exception("Expected failure - this is OK")


@contextmanager
def expect_failure_nope():
    try:
        yield
    finally:
        pass


if opts.force:
    expect_failure = expect_failure_nope


#################################################


def helper(orig_fn, *args, **kw):
    while hasattr(orig_fn, '_previous'):
        orig_fn = orig_fn._previous
    a = inspect.getargspec(orig_fn)
    _locals = dict(zip(a.args[-len(a.defaults):], a.defaults)) if a.defaults else {}
    _locals.update(dict(zip(a.args, args)))
    _locals.update(kw)
    lg = globals().copy()
    lg.update(_locals)
    return _locals, lg


def pre(expr):
    def decorator(fn):
        code = compile(expr, '<string>', 'eval')

        @wraps(fn)
        def inner(*args, **kw):
            lg = None
            try:
                orig_fn = inner
                while hasattr(orig_fn, '_previous'):
                    orig_fn = orig_fn._previous
                _locals, lg = helper(orig_fn, *args, **kw)
                assert eval(code, globals(), _locals)
            except Exception as e:
                msg = expr + "\n" + pprint.pformat(lg)
                if not isinstance(e, AssertionError):
                    msg += "\n" + repr(e)
                raise AssertionError(msg)
            return fn(*args, **kw)

        inner._previous = fn
        return inner
    return decorator


def post(expr):
    def decorator(fn):
        code = compile(expr, '<string>', 'eval')
        _globals = globals().copy()

        @wraps(fn)
        def inner(*args, **kw):
            lg = None
            try:
                kw['RETURN'] = retval = fn(*args, **kw)
                _locals, lg = helper(inner, *args, **kw)
                assert eval(code, _globals, _locals)
            except Exception as e:
                msg = expr + "\n" + pprint.pformat(lg)
                if not isinstance(e, AssertionError):
                    msg += "\n" + repr(e)
                raise AssertionError(msg)
            return retval

        inner._previous = fn
        return inner
    return decorator







# def post(expr):
#     def decorator(fn):
#         code = compile(expr, '<string>', 'eval')
#         _globals = globals().copy()
#         a = inspect.getargspec(fn)
#         localnames = a.args
#         kwdefaults = dict(zip(a.args[-len(a.defaults):], a.defaults)) if a.defaults else {}
#
#         @wraps(fn)
#         def inner(*args, **kw):
#             a = inspect.getargspec(i)
#             _locals = dict(zip(a.args[-len(a.defaults):], a.defaults)) if a.defaults else {}
#             _locals.update(dict(zip(a.args, args)))
#             _locals.update(kw)
#             _locals = kwdefaults
#             _locals.update(dict(zip(localnames, args)))
#             _locals.update(kw)
#             _locals['RETURN'] = retval = fn(*args, **kw)
#             lg = _locals.copy()
#             lg.update(_globals)
#             try:
#                 assert eval(code, _globals, _locals)
#             except Exception as e:
#                 msg = expr + "\n" + pprint.pformat(lg)
#                 if not isinstance(e, AssertionError):
#                     msg += "\n" + repr(e)
#                 raise AssertionError(msg)
#             return retval
#         inner._previous = fn
#         return inner
#     return decorator


@pre("x * x + y * y < 1.000000001")
@post("isinstance(RETURN, str)")
def quux(x, y):
    if _bad_return_value:
        return 19
    else:
        return 'OK'


print quux(1, 0)

with expect_failure():
    print quux(1, 2)

with expect_failure():
    with misbehave():
        print quux(0.3, 0.5)
