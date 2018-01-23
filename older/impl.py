import pytest
import zope.interface
from zope.interface.exceptions import BrokenImplementation
from zope.interface.verify import verifyObject


# pylint: disable=inherit-non-class
class IFoo(zope.interface.Interface):
    """Foo blah blah"""

    x = zope.interface.Attribute("""X blah blah""")

    def bar(self, q, r=None):
        """bar blah blah"""

# pylint: enable=inherit-non-class


def test_ifoo():
    x = IFoo.x
    assert type(x) == zope.interface.interface.Attribute
    assert x.__name__ == 'x'
    assert x.__doc__ == 'X blah blah'

    lst = list(IFoo)
    lst.sort()
    assert lst == ['bar', 'x']


class Foo(object):
    zope.interface.implements(IFoo)

    def __init__(self, x=None):
        self.x = x

    def bar(self, q, r=None):
        return q, r, self.x

    def __repr__(self):
        return "Foo(%s)" % self.x


def test_foo():
    # pylint: disable=no-value-for-parameter
    assert IFoo.implementedBy(Foo)
    # pylint: enable=no-value-for-parameter


class Foo2(object):
    zope.interface.implements(IFoo)    # no it doesn't

    x = 1

    def __init__(self):
        self.y = 2


def test_foo2():
    with pytest.raises(BrokenImplementation):
        verifyObject(IFoo, Foo2())
