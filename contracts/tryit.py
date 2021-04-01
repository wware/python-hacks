import inspect
import os
import re
import pprint
import unittest
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

"""
This is stuff for functions that enforce contractual agreements.
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


__contracts = {}


def _set_up_conditions(docstr):
    def _compile(expr):
        try:
            return compile(expr, "<string>", "eval")
        except Exception as e:
            raise e.__class__(expr)

    def extract_contracts():
        lines = [L.rstrip() for L in docstr.split('\n')]
        headers = {'pre', 'post', 'invariant'}
        _contracts = {}
        while headers:
            h = headers.pop()
            yaml_candidate = [i for (i, L) in enumerate(lines)
                              if re.search(h + r":$", L.rstrip())]
            if yaml_candidate:
                yaml_lines = lines[yaml_candidate[0]:]
                while len(yaml_lines) > 1:
                    try:
                        _contracts.update(yaml.load(
                            "\n".join(yaml_lines),
                            Loader=yaml.SafeLoader
                        ))
                        headers = headers.difference(_contracts.keys())
                        break
                    except:
                        pass
                    yaml_lines = yaml_lines[:-1]
        return _contracts

    frame = inspect.currentframe(2)
    locals = frame.f_locals
    globals = frame.f_globals
    co = frame.f_code
    func_name = co.co_name
    if not __contracts.has_key(id(frame)):
        contracts = {
            key: {
                (func_name, expr): _compile(expr)
                for expr in value
            }
            for key, value in extract_contracts().items()
        }
        contracts["invariant_values"] = {}
        contracts["locals"] = locals
        contracts["test_invariant"] = compile(
            "__oldvalue == __newvalue", "<string>", "eval"
        )
        __contracts[id(frame)] = contracts
    return locals, globals, func_name, frame


def _check_condition(expr, p, locals, exc):
    try:
        assert eval(p, globals(), locals)
    except Exception as e:
        msg = str(expr) + "\n" + pprint.pformat(locals)
        if not isinstance(e, AssertionError):
            msg += "\n" + repr(e)
        raise exc(msg)


def check_pre_conditions(docstr):
    locals, globals, name, frame = _set_up_conditions(docstr)
    contracts = __contracts[id(frame)]
    for expr, p in contracts.get('pre', {}).items():
        _check_condition(expr, p, locals, PreConditionFailed)
    for (func, expr), p in contracts.get('invariant', {}).items():
        contracts["invariant_values"][(func, expr)] = eval(p, globals, {})


def check_post_conditions(ret_val, docstr):
    locals, globals, name, frame = _set_up_conditions(docstr)
    locals['RETURN'] = ret_val
    contracts = __contracts[id(frame)]
    for expr, p in contracts.get('post', {}).items():
        _check_condition(expr, p, locals, PostConditionFailed)
    oldguys = contracts["invariant_values"]
    test_invariant = contracts["test_invariant"]
    for (func, expr), oldvalue in oldguys.items():
        newvalue = eval(expr, globals, {})
        locals.update({
            "__oldvalue": oldvalue,
            "__newvalue": newvalue
        })
        _check_condition((func, expr), test_invariant,
                         locals, InvariantChanged)
    return ret_val


################################


IMPLACABLE = 'this value does not change and is therefore invariant'


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
    check_pre_conditions(simplest.__doc__)
    return check_post_conditions(x + y, simplest.__doc__)


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
    check_pre_conditions(example_function.__doc__)
    return_val = int(11 + 0 * (a + b + c).real)
    if BAD1:
        return_val = 2   # violate post condition
    if BAD2:
        state_capitals.append('Bangor')    # violate invariant
    return check_post_conditions(return_val, example_function.__doc__)


def example_2(x):
    """
    If we use the explicit check... functions, we can access the function's
    internal local variables, which are not reachable by the decorator. Here
    we are accessing 'y'.

    post:
        - x + y < 12
    """
    check_pre_conditions(example_2.__doc__)
    y = x + 3
    return check_post_conditions(x + y, example_2.__doc__)


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
    check_pre_conditions(example_3.__doc__)
    return check_post_conditions(x * y * z, example_3.__doc__)


class MethodExample(object):
    def mymethod(self, x, y):
        """
        pre:
            - isinstance(x, int)
            - -5 <= x <= 5
            - isinstance(y, int)
            - -5 <= y <= 5
        post:
            - isinstance(RETURN, int)
            - -10 <= RETURN <= 10
        """
        check_pre_conditions(simplest.__doc__)
        return check_post_conditions(x + y, simplest.__doc__)


###########################################################################


def run_example():
    a = 600 if BAD3 else 3
    return example_function(a, 11.0, 3.0 + 4.0j,
                            {}, ['1', 2, 3, 4], ())


class SimpleTestCase(unittest.TestCase):

    def test_simple_clean(self):
        self.assertEqual(simplest(3, 4), 7)

    def test_simple_bad1(self):
        self.assertRaises(PreConditionFailed,
                          lambda: simplest(3.14159, 'abc'))

    def test_simple_bad2(self):
        self.assertRaises(PreConditionFailed,
                          lambda: simplest(2, 11))

    def test_1_clean(self):
        global BAD1, BAD2, BAD3
        BAD1 = BAD2 = BAD3 = False
        self.assertEqual(run_example(), 11)

    def test_1_bad1(self):
        global BAD1, BAD2, BAD3
        BAD1 = True
        BAD2 = BAD3 = False
        self.assertRaises(PostConditionFailed, run_example)

    def test_1_bad2(self):
        global BAD1, BAD2, BAD3
        BAD2 = True
        BAD1 = BAD3 = False
        self.assertRaises(InvariantChanged, run_example)

    def test_1_bad3(self):
        global BAD1, BAD2, BAD3
        BAD3 = True
        BAD1 = BAD2 = False
        self.assertRaises(PreConditionFailed, run_example)

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

    def test_method_clean(self):
        mm = MethodExample()
        self.assertEqual(mm.mymethod(3, 4), 7)

    def test_method_bad1(self):
        mm = MethodExample()
        self.assertRaises(PreConditionFailed,
                          lambda: mm.mymethod(3.14159, 'abc'))

    def test_method_bad2(self):
        mm = MethodExample()
        self.assertRaises(PreConditionFailed,
                          lambda: mm.mymethod(2, 11))


if __name__ == "__main__":
    unittest.main()
