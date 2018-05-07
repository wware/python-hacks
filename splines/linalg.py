import os
import random
import time
import unittest
from math import cos, sin, pi


class Vector(list):
    def __init__(self, *params):
        if len(params) > 1:
            list.__init__(self, params)
        else:
            list.__init__(self, *params)

    def __repr__(self):
        return "<Vector " + ", ".join(["{0}".format(x) for x in self]) + ">"

    @classmethod
    def unit_vectors(cls):
        return (cls(1, 0, 0), cls(0, 1, 0), cls(0, 0, 1))

    @classmethod
    def zero(cls):
        return cls(0, 0, 0)

    def __add__(self, other):
        return apply(self.__class__, [x + y for x, y in zip(self, other)])

    def __sub__(self, other):
        return apply(self.__class__, [x - y for x, y in zip(self, other)])

    def __neg__(self):
        return apply(self.__class__, [-x for x in self])

    def dot(self, other):
        return sum([x * y for x, y in zip(self, other)])

    def as_matrix(self):
        return Matrix(self, rows=len(self), cols=1)

    def __eq__(self, other):
        return sum([(x - y) ** 2 for x, y in zip(self, other)]) < 1.e-20


class VectorTest(unittest.TestCase):
    def test1(self):
        v1 = Vector(1, 2, 3)
        v2 = Vector(4, 6, 8)
        assert v1 + v2 == Vector(5, 8, 11)

    def test2(self):
        v1 = Vector(1, 2, 3)
        v2 = Vector(4, 6, 8)
        assert v2 - v1 == Vector(3, 4, 5)

    def test3(self):
        v1 = Vector(1, 2, 3)
        v2 = Vector(4, 6, 8)
        assert v1.dot(v2) == 40


class Matrix(Vector):
    def __init__(self, *params, **kw):
        assert kw.has_key('rows')
        assert kw.has_key('cols')
        Vector.__init__(self, *params)
        self._rows = kw['rows']
        self._cols = kw['cols']

    @classmethod
    def three(cls, *params):
        return cls(*params, rows=3, cols=3)

    @classmethod
    def four(cls, *params):
        return cls(*params, rows=4, cols=4)

    @classmethod
    def rotate_x(cls, theta):
        ct, st = cos(theta * pi / 180), sin(theta * pi / 180)
        return cls([1, 0, 0, 0, ct, -st, 0, st, ct], rows=3, cols=3)

    @classmethod
    def rotate_y(cls, theta):
        ct, st = cos(theta * pi / 180), sin(theta * pi / 180)
        return cls([ct, 0, -st, 0, 1, 0, st, 0, ct], rows=3, cols=3)

    @classmethod
    def rotate_z(cls, theta):
        ct, st = cos(theta * pi / 180), sin(theta * pi / 180)
        return cls([ct, -st, 0, st, ct, 0, 0, 0, 1], rows=3, cols=3)

    def __add__(self, other):
        assert self._rows == other._rows, (self._rows, other._rows)
        assert self._cols == other._cols, (self._cols, other._cols)
        return Matrix(Vector.add(self, other), rows=self._rows, cols=self._cols)

    def __sub__(self, other):
        assert self._rows == other._rows, (self._rows, other._rows)
        assert self._cols == other._cols, (self._cols, other._cols)
        return Matrix(Vector.sub(self, other), rows=self._rows, cols=self._cols)

    def __mul__(self, other):
        if isinstance(other, Matrix):
            assert self._cols == other._rows, (self._cols, other._rows)
            return Matrix([
                sum([
                    self[k + self._cols * row] * other[col + other._cols * k]
                    for k in xrange(self._cols)
                ])
                for row in xrange(self._rows)
                for col in xrange(other._cols)
            ], rows=self._rows, cols=other._cols)
        elif isinstance(other, Vector):
            assert self._cols == len(other), (self._cols, len(other))
            return Vector([
                sum([
                    self[self._cols * row + i] * other[i]
                    for i in xrange(self._cols)
                ])
                for row in xrange(self._rows)
            ])
        elif isinstance(other, (int, float)):
            return Matrix([
                self[self._cols * row + col] * other
                for row in xrange(self._rows)
                for col in xrange(other._cols)
            ], rows=self._rows, cols=other._cols)
        else:
            raise TypeError(other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        else:
            raise TypeError(other)

    def __repr__(self):
        return "<Matrix {0} rows={1} cols={2}>".format(list(self), self._rows, self._cols)


class MatrixTest(unittest.TestCase):
    def check(self, this, that):
        assert this == that, (this, that)

    def test1(self):
        m1 = Matrix(1, 0, 0, 0, 2, 0, rows=2, cols=3)
        m2 = Matrix(7, 8, 9, 10, 11, 12, rows=3, cols=2)
        assert m1 * m2 == Matrix(7, 8, 18, 20, rows=2, cols=2)

    def test2(self):
        m1 = Matrix.rotate_x(90)
        self.check(m1 * Vector(1, 2, 3), Vector(1, -3, 2))
        self.check(m1 * Vector(3, 2, 1), Vector(3, -1, 2))
        m1 = Matrix.rotate_x(3)
        self.check(m1 * Vector(1, 2, 3), Vector(1, 1.8402512007803162, 3.100560516749609))
        self.check(m1 * Vector(3, 2, 1), Vector(3, 1.944923113266204, 1.1033014472404614))


if __name__ == "__main__":
    import nose
    nose.main(argv=["--verbosity=3", os.path.abspath(__file__)])
