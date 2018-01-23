import unittest


def memoize(func):
    from functools import wraps
    cache = {}

    def short(x, primitive=(int, long, float, str, complex, unicode, bool)):
        return x if isinstance(x, primitive) else id(x)

    @wraps(func)
    def newfunc(*args, **kwargs):
        key = (
            tuple([short(x) for x in args]) +
            tuple([(short(k), short(v)) for k, v in kwargs.items()])
        )
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
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


def get_cache(memoized):
    F = memoized.fget
    d = dict(zip(F.func_code.co_freevars, [cell.cell_contents for cell in F.func_closure]))
    return d['cache']


class MemoizeTest(unittest.TestCase):

    def test1(self):
        foo = Foo()
        key = (id(foo),)
        cache = get_cache(Foo.my_tuple)
        self.assertTrue(key not in cache)
        self.assertEqual(foo.my_tuple, ('a', 'b', 'c'))
        self.assertEqual(cache[key], ('a', 'b', 'c'))
        self.assertEqual(foo.my_tuple, ('a', 'b', 'c'))
        self.assertEqual(cache[key], ('a', 'b', 'c'))

    def test2(self):
        foo = Foo()
        key = (id(foo),)
        cache = get_cache(Foo.my_none)
        self.assertTrue(key not in cache)
        self.assertEqual(foo.my_none, None)
        self.assertEqual(cache[key], None)
        self.assertEqual(foo.my_none, None)
        self.assertEqual(cache[key], None)


print "To test this, type: nosetests memoize.py"
