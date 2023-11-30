# runpy27.sh python -m pytest --doctest-modules pojo.py
# runpy27.sh python -m pytest testing/test_pojo.py

"""
This is a Pydantic-style field-validating frozen class for Python 2.
When you create an instance, all the arguments are validated by type, and
there must be the correct number of arguments, otherwise raises TypeError.

    >>> class Foo(Pojo):
    ...     __fields__ = [("x", int),
    ...                   ("y", float),
    ...                   ("z", str)]
    >>> foo = Foo(12, 23.456, "howdy")
    >>> foo.x
    12
    >>> foo.y
    23.456
    >>> foo.z
    'howdy'

You can treat x, y, and z as standard attributes of the foo instance.
You can define a validator function if you want more specificity.

    >>> class Foo(Pojo):
    ...     def _positive_even_integer(x):
    ...         return isinstance(x, int) and x > 0 and (x % 2) == 0
    ...     __fields__ = [("x", _positive_even_integer)]
    >>> Foo(12)
    <pojo.Foo object at 0x...>
    >>> Foo("12")
    Traceback (most recent call last):
        ...
    TypeError: ...
    >>> Foo(13)
    Traceback (most recent call last):
        ...
    TypeError: ...
    >>> Foo(-12)
    Traceback (most recent call last):
        ...
    TypeError: ...

A Pojo can use another Pojo as a field, with nested validation.

    >>> class Bar(Pojo):
    ...     __fields__ = [("x", int)]
    >>> class Nope(Pojo):
    ...     __fields__ = [("x", int)]
    >>> class Foo(Pojo):
    ...     __fields__ = [("bar", Bar)]
    >>> Foo(Bar(12))
    <pojo.Foo object at 0x...>
    >>> Foo(Nope(12))
    Traceback (most recent call last):
        ...
    TypeError: ...
    >>> Foo(Bar("12"))
    <pojo.Foo object at 0x...>

If necessary and possible, we coerce arguments to the right type,
but we don't want to get too clever with that. Follow the principle
of least surprise.

    >>> class Foo(Pojo):
    ...     __fields__ = [("x", int),
    ...                   ("y", float),
    ...                   ("z", str)]
    ... 
    >>> # x: str coerced to int
    >>> Foo("12", 23.456, "howdy")
    <pojo.Foo object at 0x...>
    >>> # y: int coerced to float
    >>> Foo(12, 23, "howdy")
    <pojo.Foo object at 0x...>
    >>> # z: complex coerced to str
    >>> Foo(12, 23.456, 3+4j)
    <pojo.Foo object at 0x...>

Tests should be
  * independent of each other
  * should not depend on the order in which tests are run
  * should not depend on the results of any other test
  * should not depend on the implementation of the code under test
  * minimal
    - fast, concise, easy to read
    - test only things that pertain directly to the intent of the test
    - don't declare variables you don't need
"""

class Pojo(object):
    def __init__(self, *args):
        if len(args) != len(self.__fields__):
            raise TypeError((args, self.__fields__))
        for arg, (name, _type) in zip(args, self.__fields__):
            import datetime
            if isinstance(_type, type):
                if _type in (int, float, complex, str):
                    try:
                        arg = _type(arg)
                    except:
                        pass
                elif _type in (datetime.date,
                               datetime.datetime,
                               datetime.timedelta):
                    # I'll get to these real soon now
                    raise NotImplementedError(_type)
                if not isinstance(arg, _type):
                    # coercion failed
                    raise TypeError((name, arg, _type))
            elif callable(_type):
                if not _type(arg):
                    raise TypeError((name, arg, _type))
            else:
                raise TypeError((name, arg, _type))
            # https://stackoverflow.com/questions/12998926#answer-12999019
            self.__dict__[name] = arg

    def __setattr__(self, name, value):
        # instances are frozen after creation
        raise TypeError(name)
