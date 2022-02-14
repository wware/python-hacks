from pytest import raises
from fp import Vector

def test_1():
    v = Vector(x=0, y=3, z=4)
    assert v.len() == 5.0

def test_2():
    v = Vector(x=0, y=3, z=4)
    assert repr(v) == "Vector(x=0, y=3, z=4)"

def test_3():
    v = Vector(x=0, y=3, z=4)
    v2 = Vector(5, 12, 13)
    assert v.inner(v2) == 88.0

def test_4():
    v = Vector(x=0, y=3, z=4)
    with raises(AttributeError):
        # attributes are read only
        v.x = 11

def test_5():
    v = Vector(x=0, y=3, z=4)
    assert v.scale(2) == Vector(0, 6, 8)

class A:
    def f(self, x):
        return self.g(x) + 1
    def g(self, y):
        return y + 2

def test_6():
    a = A()
    assert a.f(1) == 4
    assert a.g(5) == 7
