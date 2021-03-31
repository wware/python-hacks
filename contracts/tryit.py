import inspect
import os
import re
import yaml
from functools import wraps


"""
# Contractual functions in Python

People call this "design by contract". The easily google-able info
about it is pretty shallow, unfortunately. But I think there is
something worthwhile there. See `tryit.py` in this directory for
the general idea.

If you want to disable the contract stuff and get back any performance
hit it might have caused, run the code with `python -O` instead of
`python`, which will turn off the `__debug__` flag.

## Why do this?

Programmers' assumptions are almost never recorded accurately or
communicated effectively. With contracts, we get:

* Each function has assumptions specified as pre-conditions and
  post-conditions and invariants.
* All these assumptions are tested on every function call all the
  time, unless explicitly switched off for performance.
* Any failed assumption provides information to minimize the
  search space for the bug.

If a post-condition fails after the pre-conditions passed, then the
function is at fault. If a pre-condition fails, then the code that
calls the function is at fault. If an invariant changes, at least you
know where to start looking.

You can mix contractual and non-contractual functions, so you don't
need to upgrade all your code before you can benefit.

Python has a magic variable called "__debug__" which controls normal
assert statements and also these contract things, and you can switch
them all off for performance by using the "-O" option when you invoke
the Python interpreter. I personally think you should keep them on all
the time, and if you have performance issues, write better code.

## Two modes

The approach here presents two modes of contracts. One uses markup in
the docstring, combined with a decorator. The other uses the same
markup but the decorator is replaced by a couple of function calls in
your function. The latter is a teeny bit more work, but it allows your
post-conditions to pull in the function's internal local variables,
which are not reachable by the decorator. So if you include an internal
variable in a post-condition and then use the decorator, you'll get an
error.
"""


def env_var(x):
    return os.environ.get(x, '') == '1'


class ContractViolation(AssertionError):
    pass


class PreConditionFailed(ContractViolation):
    pass


class PostConditionFailed(ContractViolation):
    pass


class InvariantChanged(ContractViolation):
    pass


__inv_stack = []


def check_pre_conditions(locals=None, docstr=None, frame_offset=1):
    def _compile(expr):
        try:
            return compile(expr, "<string>", "eval")
        except Exception as e:
            raise e.__class__(expr)

    """
    When using decorator:
      - locals are passed in, and represent arguments, WORKS OK
      - docstring is passed in, WORKS OK
      - function name seems WRONG -- wraps(func) is not working right???
      - inspect.currentframe(xxx) is pulling from the ... oh yeah ... fix this
      - I want the frame in which the decorated function is defined so PASS THAT IN
         - can I derive locals and docstr from that frame??? yes I can
         - if I DO NOT get said frame, locals and docstr come from the frame
           that called me
    """

    fr = inspect.currentframe(frame_offset)
    if not fr.f_locals.has_key('__co_contracts'):
        if locals is None:
            locals = fr.f_locals
        if docstr is None:
            docstr = fr.f_globals[fr.f_code.co_name].__doc__
        globals = {}
        for i in range(frame_offset + 1):
            globals.update(inspect.currentframe(i).f_globals)
        contracts = {
            key: {
                fr.f_code.co_name + ": " + expr: _compile(expr)
                for expr in value
            }
            for key, value in extract_contracts(docstr).items()
        }
        contracts['globals'] = globals
        fr.f_locals['__co_contracts'] = contracts

    contracts = fr.f_locals['__co_contracts']
    globals = contracts['globals']
    lg = locals.copy()
    lg.update(globals)
    for expr, p in contracts.get('pre', {}).items():
        try:
            assert eval(p, globals, locals)
        except Exception as e:
            msg = expr + "\n" + pprint.pformat(lg)
            if not isinstance(e, AssertionError):
                msg += "\n" + repr(e)
            raise PreConditionFailed(msg)
    inv = {}
    for expr, p in contracts.get('invariant', {}).items():
        inv[expr] = eval(p, globals, {})
    __inv_stack.append(inv)


def check_post_conditions(ret_val, locals=None, frame_offset=1):
    fr = inspect.currentframe(frame_offset)
    if locals is None:
        locals = fr.f_locals
    contracts = fr.f_locals['__co_contracts']
    locals = locals.copy()
    locals['RETURN'] = ret_val
    globals = contracts['globals']
    lg = locals.copy()
    lg.update(globals)
    for expr, p in contracts.get('post', {}).items():
        try:
            assert eval(p, globals, locals)
        except Exception as e:
            msg = expr + "\n" + pprint.pformat(lg)
            if not isinstance(e, AssertionError):
                msg += "\n" + repr(e)
            raise PostConditionFailed(msg)
    inv = __inv_stack.pop()
    newguys = contracts.get('invariant', {})
    for expr in inv.keys():
        newer = newguys.get(expr, 'None')
        try:
            assert inv[expr] == eval(newer, globals, {})
        except Exception as e:
            msg = expr + "\n" + pprint.pformat(lg)
            if not isinstance(e, AssertionError):
                msg += "\n" + repr(e)
            raise InvariantChanged(msg)


def enforce_contract(func):
    """
    This is a decorator for functions that enforce contractual agreements.
    Functions define a contract with the code that calls them by creating
    pre- and post-conditions and invariants. The pre-conditions are things the
    function requires of the calling code, and post-conditions are promises of
    what the function will deliver. Invariants are promises to avoid causing
    side effects. Contracts go in docstrings and are specified in YAML.

    pre:
      - isinstance(a, int)
      - isinstance(b, float)
      - isinstance(c, complex)
      - isinstance(x, dict)
      - isinstance(y, list)
      - isinstance(z, tuple)
      - (a ** 2 + b ** 2 + (c ** 2).real) < 2500
      - len(y) > 3
      - all([isinstance(y, str) for z in y])
    post:
      - (RETURN ** 2 + a ** 2) > 16
    invariant:
      # things that should not be changed by this function
      - len(state_capitals)

    If you write functions with contracts and you want to switch them off for
    performance reasons, run Python with the "-O" option, setting the __debug__
    variable to False.
    """
    if not __debug__:
        return func

    a = inspect.getargspec(func)
    localnames = a.args
    kwdefaults = dict(zip(a.args[-len(a.defaults):], a.defaults)) if a.defaults else {}

    @wraps(func)
    def inner(*args, **kw):
        locals = kwdefaults
        locals.update(dict(zip(localnames, args)))
        locals.update(kw)
        check_pre_conditions(locals, func.__doc__, 2)
        return_val = func(*args, **kw)
        check_post_conditions(return_val, locals, 2)
        return return_val
    return inner





def extract_contracts(docstr):
    lines = [L.rstrip() for L in docstr.split('\n')]
    headers = set(['pre', 'post', 'invariant'])
    contracts = {}
    while headers:
        h = headers.pop()
        p = [i for (i, L) in enumerate(lines) if re.search(h + ":$", L)]
        if p:
            yaml_lines = lines[p[0]:]
            while len(yaml_lines) > 1:
                try:
                    contracts.update(yaml.load(
                        "\n".join(yaml_lines),
                        Loader=yaml.SafeLoader
                    ))
                    headers = headers.difference(contracts.keys())
                    break
                except:
                    pass
                yaml_lines = yaml_lines[:-1]
    return contracts


__inv_stack = []


def check_pre_conditions(locals=None, docstr=None, frame_offset=1):
    fr = inspect.currentframe(frame_offset)
    if locals is None:
        locals = fr.f_locals
    if docstr is None:
        docstr = fr.f_globals[fr.f_code.co_name].__doc__
    contracts = extract_contracts(docstr)
    for p in contracts.get('pre', []):
        if not eval(p, fr.f_globals, locals):
            raise PreConditionFailed(p)
    inv = []
    for p in contracts.get('invariant', []):
        inv.append(eval(p, fr.f_globals, {}))
    __inv_stack.append(tuple(inv))


def check_post_conditions(ret_val, locals=None, docstr=None, frame_offset=1):
    fr = inspect.currentframe(frame_offset)
    if locals is None:
        locals = fr.f_locals
    if docstr is None:
        docstr = fr.f_globals[fr.f_code.co_name].__doc__
    contracts = extract_contracts(docstr)
    locals = locals.copy()
    locals['RETURN'] = ret_val
    for p in contracts.get('post', []):
        if not eval(p, fr.f_globals, locals):
            raise PostConditionFailed(p)
    inv = __inv_stack.pop()
    for old, p in zip(inv, contracts.get('invariant', [])):
        x = eval(p, fr.f_globals, {})
        if old != x:
            raise InvariantChanged(p)


def enforce_contract(func):
    """
    This is a decorator for functions that enforce contractual agreements.
    Functions define a contract with the code that calls them by creating
    pre- and post-conditions and invariants. The pre-conditions are things the
    function requires of the calling code, and post-conditions are promises of
    what the function will deliver. Invariants are promises to avoid causing
    side effects. Contracts go in docstrings and are specified in YAML.

    pre:
      - isinstance(a, int)
      - isinstance(b, float)
      - isinstance(c, complex)
      - isinstance(x, dict)
      - isinstance(y, list)
      - isinstance(z, tuple)
      - (a ** 2 + b ** 2 + (c ** 2).real) < 2500
      - len(y) > 3
      - all([isinstance(y, str) for z in y])
    post:
      - (RETURN ** 2 + a ** 2) > 16
    invariant:
      # things that should not be changed by this function
      - len(state_capitals)

    If you write functions with contracts and you want to switch them off for
    performance reasons, run Python with the "-O" option, setting the __debug__
    variable to False.
    """
    if not __debug__:
        return func

    def make_locals(args, kw):
        locals = dict(zip(func.func_code.co_varnames, args))
        locals.update(kw)
        return locals

    @wraps(func)
    def inner(*args, **kw):
        check_pre_conditions(make_locals(args, kw), func.__doc__, 2)
        return_val = func(*args, **kw)
        check_post_conditions(return_val, make_locals(args, kw), func.__doc__, 2)
        return return_val
    return inner


################################


IMPLACABLE = 'this value does not change and is therefore invariant'


@enforce_contract
def simplest(x, y):
    """
    This is a nice simple case. Notice that the post conditions do not reference
    any variables except the function arguments and the return value.

    pre:
        - isinstance(x, int)
        - -5 <= x <= 5
        - isinstance(y, int)
        - -5 <= y <= 5
    post:
        - isinstance(RETURN, int)
        - -10 <= RETURN <= 10
    invariant:
        - IMPLACABLE
    """
    return x + y



DECORATOR = False
BAD1 = BAD2 = BAD3 = False

state_capitals = ['Boston', 'Hartford']

def example_function(a, b, c, x, y, z, plugh=None):
    """
    Random information about the function...

    Pre-conditions can simply be the types of arguments, or they can
    talk about multiple arguments at a time, for instance something like
    "the point (x, y) needs to be inside the unit circle"
    pre:
        - isinstance(a, int)
        - isinstance(b, float)
        - isinstance(c, complex)
        - isinstance(x, dict)
        - isinstance(y, list)
        - isinstance(z, tuple)
        - (a ** 2 + b ** 2 + (c ** 2).real) < 2500
        - len(y) > 3
        - isinstance(y[0], str)

    Post-conditions are promises that the function makes to the calling
    code, provided the pre-conditions are all met.
    post:
        - (RETURN ** 2 + a ** 2) > 16

    The purpose of invariants is to show that a function avoids undesirable
    side effects.
    invariant:
        # things that should not be changed by this function
        - len(state_capitals)
    """
    # use x, y, and z, for nothing, to avoid a pycharm warning
    x.update({'silly': y + list(z), 'extra': plugh})
    if not DECORATOR:
        check_pre_conditions()
    return_val = int(11 + 0 * (a + b + c).real)
    if BAD1:
        return_val = 2   # violate post condition
    if BAD2:
        state_capitals.append('Bangor')    # violate invariant
    if not DECORATOR:
        check_post_conditions(return_val)
    return return_val


example_decorated = enforce_contract(example_function)


def example_2(x):
    """
    If we use the explicit check... functions, we can access the function's
    internal local variables, which are not reachable by the decorator. Here
    we are accessing 'y'.

    post:
        - x + y < 12
    """
    check_pre_conditions()
    y = x + 3
    z = x + y
    check_post_conditions(z)
    return z


def example_3(x, y=1, z=2, **kw):
    """
    pre:
        - y < 5
        - z < 5
        - len(kw.keys()) < 2
    post:
        - x + y + z < 15
        - RETURN < 15
    """
    check_pre_conditions()
    w = x * y * z
    check_post_conditions(w)
    return w


###########################################################################


import unittest


class SimpleTestCase(unittest.TestCase):
    def run_example(self):
        a = 600 if BAD3 else 3
        return example_function(a, 11.0, 3.0 + 4.0j,
                                {}, ['1', 2, 3, 4], ())

    def run_decorated(self):
        a = 600 if BAD3 else 3
        return example_decorated(a, 11.0, 3.0 + 4.0j,
                                 {}, ['1', 2, 3, 4], ())

    def test_simple_clean(self):
        self.assertEqual(simplest(3, 4), 7)

    def test_simple_bad1(self):
        self.assertRaises(PreConditionFailed,
                          lambda: simplest(3.14159, 'abc'))

    def test_simple_bad2(self):
        self.assertRaises(PreConditionFailed,
                          lambda: simplest(2, 11))

    def test_1_clean(self):
        global BAD1, BAD2, BAD3, DECORATOR
        BAD1 = BAD2 = BAD3 = DECORATOR = False
        self.assertEqual(self.run_example(), 11)

    def test_1_bad1(self):
        global BAD1, BAD2, BAD3, DECORATOR
        BAD1 = True
        BAD2 = BAD3 = DECORATOR = False
        self.assertRaises(PostConditionFailed, self.run_example)

    def test_1_bad2(self):
        global BAD1, BAD2, BAD3, DECORATOR
        BAD2 = True
        BAD1 = BAD3 = DECORATOR = False
        self.assertRaises(InvariantChanged, self.run_example)

    def test_1_bad3(self):
        global BAD1, BAD2, BAD3, DECORATOR
        BAD3 = True
        BAD1 = BAD2 = DECORATOR = False
        self.assertRaises(PreConditionFailed, self.run_example)

    def test_1d_clean(self):
        global BAD1, BAD2, BAD3, DECORATOR
        BAD1 = BAD2 = BAD3 = False
        DECORATOR = True
        self.assertEqual(self.run_decorated(), 11)

    def test_1d_bad1(self):
        global BAD1, BAD2, BAD3, DECORATOR
        BAD1 = True
        BAD2 = BAD3 = False
        DECORATOR = True
        self.assertRaises(PostConditionFailed, self.run_decorated)

    def test_1d_bad2(self):
        global BAD1, BAD2, BAD3, DECORATOR
        BAD2 = True
        BAD1 = BAD3 = False
        DECORATOR = True
        self.assertRaises(InvariantChanged, self.run_decorated)

    def test_1d_bad3(self):
        global BAD1, BAD2, BAD3, DECORATOR
        BAD3 = True
        BAD1 = BAD2 = False
        DECORATOR = True
        self.assertRaises(PreConditionFailed, self.run_decorated)

    def test_2_good(self):
        self.assertEqual(example_2(1), 5)

    def test_2_bad(self):
        self.assertRaises(PostConditionFailed, lambda: example_2(25))

    def test_3_good(self):
        self.assertEqual(example_3(1), 2)

    def test_3_bad1(self):
        self.assertRaises(PreConditionFailed, lambda: example_3(1, 12, 100))

    def test_3_bad2(self):
        self.assertRaises(PreConditionFailed,
                          lambda: example_3(1, 1, 2,
                                            a='hi', b='bye', c='ouch'))

if __name__ == "__main__":
    unittest.main()
