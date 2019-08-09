from contextlib import contextmanager
import contracts
import sys

if '--no-contracts' in sys.argv[1:]:
    contracts.disable_all()

@contracts.contract(x='int', y='int', returns='int')
def add(x, y, misbehave=False):
    if misbehave:
        return 'OOPS'    # string, should be int
    else:
        return x + y

@contextmanager
def expect_failure():
    success = True
    try:
        yield
    except:
        success = False
    assert not success

add(3, 5)            # this is ok

with expect_failure():
    add(1.2, 4.7)    # arguments aren't ints

with expect_failure():
    add(3, 5, misbehave = True)    # bad return value

#########################

contracts.new_contract('even', lambda x: (x % 2) == 0)

@contracts.contract(x='int,<=0,even', y='int,<=0', returns='int,>=0')
def mulneg(x, y):
    return x * y

assert mulneg(-2, -3) == 6
assert mulneg(0, 0) == 0
assert mulneg(0, -4) == 0

with expect_failure():
    assert mulneg(2, -3) == -6    # 2 > 0

with expect_failure():
    assert mulneg(-1, -3) == 3    # -1 is not even

#########################

class Foo(object):
    def __init__(self):
        self.state = 'BAD'

    @property
    @contracts.contract(returns='validState')
    def state(self):
        return self._state

    @state.setter
    @contracts.contract(value='validState')
    @contracts.contract(returns='None')
    def state(self, value):
        self._state = value

@contracts.new_contract
def isGood(x):
    return x._state == 'GOOD'

@contracts.new_contract
def validState(x):
    return x in ('GOOD', 'BAD')

contracts.new_contract('Foo', Foo)

class Bar(object):
    pass

@contracts.contract(foo='Foo,isGood')
def require_good_foo(foo):
    pass

z = Foo()

with expect_failure():
    z.state = 'HALF-BAKED'   # valid states are GOOD and BAD

with expect_failure():
    require_good_foo(z)      # default state is BAD

z.state = 'GOOD'

require_good_foo(z)

with expect_failure():
    require_good_foo(Bar())     # fails because argument must be a Foo

@contracts.contract(foo='Foo')
@contracts.contract(returns='Foo,isGood')
def make_foo_great_again(foo, misbehave=False):
    foo.state = 'BAD' if misbehave else 'GOOD'
    return foo

z = Foo()

assert z.state == 'BAD'

make_foo_great_again(z)

assert z.state == 'GOOD'

with expect_failure():
    make_foo_great_again(z, misbehave=True)

assert z.state == 'BAD'
