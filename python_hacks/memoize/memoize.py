import unittest
from functools import wraps

_cache = {}


def memoize(func):
    """
    Decorator that memoizes a function. The memoized function can use "fresh=True"
    to avoid using cached results.
    @param func: the function to be memoized
    @return: the function with memoization
    """

    def short(x, primitive=(int, long, float, str, complex, unicode, bool)):
        return x if isinstance(x, primitive) else id(x)

    @wraps(func)
    def newfunc(*args, **kwargs):
        fresh = kwargs.pop('fresh', False)
        key = (id(func), ) + (
            tuple([short(x) for x in args]) +
            tuple([(short(k), short(v)) for k, v in kwargs.items()])
        )
        if fresh or key not in _cache:
            _cache[key] = func(*args, **kwargs)
        return _cache[key]
    return newfunc


class Foo(object):
    _my_a = 'a'
    _my_b = 'b'
    _my_c = 'c'

    @property
    @memoize
    def my_tuple(self):
        return (self._my_a, self._my_b, self._my_c)

    @property
    @memoize
    def my_none(self):
        return None


class MemoizeTest(unittest.TestCase):

    def test1(self):
        foo = Foo()
        self.assertEqual(foo.my_tuple, ('a', 'b', 'c'))
        my_tuple = Foo.my_tuple.fget.func_closure[0].cell_contents
        key = (id(my_tuple), id(foo),)
        self.assertEqual(_cache[key], ('a', 'b', 'c'))
        self.assertEqual(foo.my_tuple, ('a', 'b', 'c'))
        self.assertEqual(_cache[key], ('a', 'b', 'c'))

    def test2(self):
        foo = Foo()
        my_none = Foo.my_none.fget.func_closure[0].cell_contents
        self.assertEqual(foo.my_none, None)
        key = (id(my_none), id(foo),)
        self.assertEqual(_cache[key], None)
        self.assertEqual(foo.my_none, None)
        self.assertEqual(_cache[key], None)


print "To test this, type: nosetests memoize.py"
