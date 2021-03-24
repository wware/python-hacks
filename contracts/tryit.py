import pprint
import os
import yaml
from functools import wraps


def env_var(x):
    return os.environ.get(x, '') == '1'


class PreConditionFailed(AssertionError):
    pass


class PostConditionFailed(AssertionError):
    pass


class InvariantChanged(AssertionError):
    pass


def enforce_contract(func):
    if not __debug__:
        return func
    lines = [L for L in func.__doc__.split('\n') if len(L) > 0]
    m = [i for (i, L) in enumerate(lines) if "<contract>" in L][0]
    n = [i for (i, L) in enumerate(lines) if "</contract>" in L][0]
    dbc_stuff = yaml.load('\n'.join(lines[m+1:n]))
    co = func.func_code
    arg_names = co.co_varnames

    @wraps(func)
    def inner(*args, **kw):
        _locals = dict(zip(arg_names, args))
        _locals.update(kw)
        inv = {}
        for i, p in enumerate(dbc_stuff['invariant']):
            inv[i] = eval(p, globals(), _locals)
        for p in dbc_stuff['pre']:
            if not eval(p, globals(), _locals):
                raise PreConditionFailed(p)
        return_val = func(*args, **kw)
        _locals['RETURN'] = return_val
        for i, p in enumerate(dbc_stuff['invariant']):
            newer = eval(p, globals(), _locals)
            if inv[i] != newer:
                raise InvariantChanged((p, inv[i], newer))
        for p in dbc_stuff['post']:
            if not eval(p, globals(), _locals):
                raise PostConditionFailed(p)
        return return_val
    return inner

################################


state_capitals = ['Boston', 'Hartford']


@enforce_contract
def example_function(a, b, c, x, y, z, plugh=None):
    """
    Random useless information about the function...

    <contract>
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
    post:
        - (RETURN ** 2 + a ** 2) > 16
    invariant:
        # things that should not be changed by this function
        - len(state_capitals)
    </contract>

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
