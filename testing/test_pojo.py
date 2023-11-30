import pytest
from pojo import Pojo

"""
## Testing notes

Tests should be

* independent of one another
* should not depend on the order in which tests are run
* should not depend on the results of any other test
* should not depend on the implementation of the code under test
* fast, concise, easy to read
* test only things that pertain directly to the intent of the test
* don't declare variables you don't need
"""


def test_empty_pojo():
    class Foo(Pojo):
        __fields__ = []
    Foo()
    with pytest.raises(TypeError):
        Foo(12)


def test_getting_fields():
    class Foo(Pojo):
        __fields__ = [("x", int),
                      ("y", float),
                      ("z", str)]
    foo = Foo(12, 23.456, "howdy")
    assert foo.x == 12
    assert foo.y == 23.456
    assert foo.z == "howdy"


def test_number_of_args():
    class Foo(Pojo):
        __fields__ = [("x", int),
                      ("y", float)]
    Foo(12, 23.456)
    with pytest.raises(TypeError):
        Foo(12)
    with pytest.raises(TypeError):
        Foo(12, 23.456, "additional")


def test_basic_validation():
    class Foo(Pojo):
        __fields__ = [("x", int),
                      ("y", float),
                      ("z", str)]
    Foo(12, 23.456, "howdy")


def test_functional_validation():
    class Foo(Pojo):
        def _positive_even_integer(x):
            try:
                x = int(x)
                return x > 0 and (x % 2) == 0
            except ValueError:
                raise TypeError(x)
        __fields__ = [("x", _positive_even_integer)]
    Foo(12)
    Foo("12")
    with pytest.raises(TypeError):
        Foo(-12)
    with pytest.raises(TypeError):
        Foo(13)


def test_type_coercion():
    class Foo(Pojo):
        __fields__ = [("x", int),
                      ("y", float),
                      ("z", str)]
    # x: str coerced to int
    foo = Foo("12", 23.456, "howdy")
    assert isinstance(foo.x, int) and foo.x == 12
    # y: int coerced to float
    foo = Foo(12, 23, "howdy")
    assert isinstance(foo.y, float) and foo.y == 23.0
    # z: complex coerced to str
    foo = Foo(12, 23.456, 3+4j)
    assert isinstance(foo.z, str) and foo.z == "(3+4j)"


def test_type_coercion_failures():
    class Foo(Pojo):
        __fields__ = [("x", int),
                      ("y", float)]
    # x: str which cannot be coerced to int
    with pytest.raises(TypeError):
        Foo("xyzzy", 23.456)
    # y: str which cannot be coerced to float
    with pytest.raises(TypeError):
        Foo(12, "xyzzy")


def test_bogus_validator():
    class Foo(Pojo):
        __fields__ = [("x", None)]
    with pytest.raises(TypeError):
        Foo()
    with pytest.raises(TypeError):
        Foo(12)


def test_pojo_instance_as_field():
    class Bar(Pojo):
        __fields__ = [("x", int)]
    class BadBar(Pojo):
        __fields__ = [("x", int)]
    class Foo(Pojo):
        __fields__ = [("bar", Bar)]
    # normal intended usage
    Foo(Bar(12))
    # bad field, should be Bar not BadBar
    with pytest.raises(TypeError):
        Foo(BadBar(12))
    # bad field, should be Bar not int
    with pytest.raises(TypeError):
        Foo(12)


def test_non_pojo_instance_as_field():
    class Bar(object):
        pass
    class BadBar(object):
        pass
    class Foo(Pojo):
        __fields__ = [("bar", Bar)]
    Foo(Bar())
    with pytest.raises(TypeError):
        Foo(BadBar())


def test_frozen_instance():
    class Foo(Pojo):
        __fields__ = [("x", int)]
    foo = Foo(12)
    assert foo.x == 12
    with pytest.raises(TypeError):
        foo.x = 14
    assert foo.x == 12


def test_frozen_nested_instance():
    class Bar(Pojo):
        __fields__ = [("x", int)]
    class Foobar(Pojo):
        __fields__ = [("bar", Bar)]
    bar = Bar(12)
    foo = Foobar(bar)
    assert foo.bar.x == 12
    with pytest.raises(TypeError):
        bar.x = 11
    with pytest.raises(TypeError):
        foo.bar = Bar(10)
    with pytest.raises(TypeError):
        foo.bar.x = 10
    assert isinstance(foo.bar, Bar)
    assert foo.bar.x == 12
