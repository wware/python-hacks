import pprint
import inspect
import os
import re
import yaml
from functools import wraps


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
    lines = [L.rstrip() for L in func.__doc__.split('\n')]
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
    co = func.func_code
    arg_names = co.co_varnames
    _globals = inspect.currentframe(1).f_globals

    @wraps(func)
    def inner(*args, **kw):
        _locals = dict(zip(arg_names, args))
        _locals.update(kw)

        def evaluate(c, ouch, _locals=_locals, _globals=_globals):
            try:
                return eval(c, _globals, _locals)
            except Exception as e:
                raise ouch(pprint.pformat((e, p, _locals, _globals)))

        inv = {}
        for i, p in enumerate(contracts.get('invariant', [])):
            inv[i] = evaluate(p, InvariantChanged)
        for p in contracts.get('pre', []):
            if not evaluate(p, PreConditionFailed):
                raise PreConditionFailed("\n" + pprint.pformat((p, _locals, _globals)))
        return_val = func(*args, **kw)
        _locals['RETURN'] = return_val
        for i, p in enumerate(contracts.get('invariant', [])):
            newer = evaluate(p, InvariantChanged)
            if inv[i] != newer:
                raise InvariantChanged("\n" + pprint.pformat((p, inv[i], newer)))
        for p in contracts.get('post', []):
            if not evaluate(p, PostConditionFailed):
                raise PostConditionFailed("\n" + pprint.pformat((p, return_val, _locals, _globals)))
        return return_val
    return inner

################################


state_capitals = ['Boston', 'Hartford']


@enforce_contract
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
    return_val = int(11 + 0 * (a + b + c).real)
    if env_var('BAD1'):
        return_val = 2   # violate post condition
    if env_var('BAD2'):
        state_capitals.append('Bangor')    # violate invariant
    return return_val


if env_var('BAD3'):
    a = 600      # violate pre condition
else:
    a = 3
print example_function(a, 11.0, 3.0 + 4.0j,
                       {}, ['1', 2, 3, 4], ())
