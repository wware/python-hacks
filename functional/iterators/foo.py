# https://pycon2019.trey.io/iterator-protocol.html

import doctest


def count(n=0):
    """
    >>> c = count()
    >>> next(c)
    0
    >>> next(c)
    1
    >>> next(c)
    2
    >>> next(c)
    3
    """
    while True:
        yield n
        n += 1


def generatorify(iterable):
    """
    >>> g = generatorify([1, 2, 3, 4])
    >>> g
    <generator object generatorify at 0x...>
    >>> next(g)
    1
    >>> next(g)
    2
    >>> for x in g:
    ...     print(x)
    ...
    3
    4
    """
    for i in iterable:
        yield i


def all_same(it):
    """
    >>> all_same(n % 2 for n in [3, 5, 7, 8])
    False
    >>> all_same(n % 2 for n in [3, 5, 7, 9])
    True
    """
    first = nope = object()
    for i in iter(it):
        if first is nope:
            first = i
        elif first != i:
            return False
    return True


"""
Next I want to do something with lazy evaluation and filtering,
where the filter lets you avoid some expensive computation.
"""


def take(n, it):
    it = iter(it)
    lst = []
    while n:
        lst.append(next(it))
        n -= 1
    return lst


def lazy_map(f, it):
    """
    >>> def make_tuples(x):
    ...   return (x, x+1)
    ...
    >>> z = lazy_map(make_tuples, count(1))
    >>> z
    <generator object lazy_map at 0x...>
    >>> take(5, z)
    [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
    """
    for i in it:
        yield f(i)


def lazy_filter(f, it):
    """
    >>> def make_tuples(x):
    ...   return (x, x+1)
    ...
    >>> def is_odd(x):
    ...   return (x % 2) != 0
    ...
    >>> z = lazy_map(make_tuples, lazy_filter(is_odd, count(1)))
    >>> z
    <generator object lazy_map at 0x...>
    >>> take(5, z)
    [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]
    """
    # The example above would have been more dramatic if "make_tuples" did
    # something really expensive, like test primality or generate an RSA key.
    for i in it:
        if f(i):
            yield i


if __name__ == '__main__':
    doctest.testmod(optionflags=doctest.ELLIPSIS)
