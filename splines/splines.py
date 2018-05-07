import os
import random
import unittest
import nose

from linalg import Vector, Matrix

# pylint: disable=bad-whitespace,invalid-name


class CubicSpline(object):
    def __init__(self, x0, xd0, x1, xd1):
        self.c = c = xd0
        self.d = d = x0
        a3b2 = xd1 - c
        ab = x1 - c - d
        self.a = a3b2 - 2 * ab
        self.b = 3 * ab - a3b2

    def __call__(self, t):
        return self.a * t**3 + self.b * t**2 + self.c * t + self.d

    def deriv(self, t):
        return 3 * self.a * t**2 + 2 * self.b * t + self.c

    @classmethod
    def testcase(cls, *params):
        s = cls(*params)
        assert (s(0), s.deriv(0), s(1), s.deriv(1)) == params
        return s

    def to_gnuplot(self, fn):
        outf = open(fn, 'w')
        n = 100
        for i in xrange(0, n + 1):
            t = 1. * i / n
            outf.write("{0} {1}\n".format(t, self(t)))
        outf.close()


class BicubicSpline(object):
    def __init__(self, *params):
        # https://en.wikipedia.org/wiki/Bicubic_interpolation
        assert len(params) == 16
        x00, x10, x01, x11, xu00, xu10, xu01, xu11, xv00, xv10, xv01, xv11, xuv00, xuv10, xuv01, xuv11 = params
        alpha = Matrix.four(
            1, 0, 0, 0,
            0, 0, 1, 0,
            -3, 3, -2, -1,
            2, -2, 1, 1
        ) * Matrix.four(
            x00, x01, xv00, xv01,
            x10, x11, xv10, xv11,
            xu00, xu01, xuv00, xuv01,
            xu10, xu11, xuv10, xuv11
        ) * Matrix.four(
            1, 0, -3, 2,
            0, 0, 3, -2,
            0, 1, -2, 1,
            0, 0, -1, 1
        )
        self.a = [alpha[:4], alpha[4:8], alpha[8:12], alpha[12:]]

    def __call__(self, u, v):
        return sum(
            [
                self.a[i][j] * u**i * v**j
                for i in range(4)
                for j in range(4)
            ]
        )

    def partial_u(self, u, v):
        return sum(
            [
                i * self.a[i][j] * u**(i-1) * v**j
                for i in range(1, 4)
                for j in range(4)
            ]
        )

    def partial_v(self, u, v):
        return sum(
            [
                j * self.a[i][j] * u**i * v**(j-1)
                for i in range(4)
                for j in range(1, 4)
            ]
        )

    def partial_uv(self, u, v):
        return sum(
            [
                i * j * self.a[i][j] * u**(i-1) * v**(j-1)
                for i in range(1, 4)
                for j in range(1, 4)
            ]
        )

    @classmethod
    def testcase(cls, *params):
        s = cls(*params)
        results = [
            s(0, 0),            s(1, 0),            s(0, 1),            s(1, 1),
            s.partial_u(0, 0),  s.partial_u(1, 0),  s.partial_u(0, 1),  s.partial_u(1, 1),
            s.partial_v(0, 0),  s.partial_v(1, 0),  s.partial_v(0, 1),  s.partial_v(1, 1),
            s.partial_uv(0, 0), s.partial_uv(1, 0), s.partial_uv(0, 1), s.partial_uv(1, 1),
        ]
        delta = 0.
        for i in xrange(16):
            delta += (results[i] - params[i]) ** 2
        assert delta < 1.e-16, delta
        return s

    def to_gnuplot(self, fn):
        outf = open(fn, 'w')
        n = 100
        for i in xrange(0, n + 1):
            for j in xrange(0, n + 1):
                u = 1. * i / n
                v = 1. * j / n
                outf.write("{0} {1} {2}\n".format(u, v, self(u, v)))
        outf.close()
        outf = open("gp.cmd", "w")
        cmd = 'splot "' + fn + '"'
        outf.write(cmd + '; pause 10;')
        outf.close()
        os.system("gnuplot gp.cmd")
        os.remove("gp.cmd")
        os.remove(fn)


class SplineTest(unittest.TestCase):
    def test1(self):
        CubicSpline.testcase(0, 1, 0, -1)

    def test2(self):
        params = [2 * random.random() - 1 for _ in range(16)]
        BicubicSpline.testcase(*params)


class Tile(object):
    class Layer(BicubicSpline):
        @classmethod
        def from_vectors(cls, A, B, C, D, E, F, G, H, I, J, K, L, fn):
            A, B, C, D, E, F, G, H, I, J, K, L = map(fn, [A, B, C, D, E, F, G, H, I, J, K, L])
            # return cls(A, B, D, C, A - E, B - F, J - D, I - C, A - L, B - G, K - D, H - C, 0, 0, 0, 0)
            return cls(
                A, B, D, C,
                A - L, G - B, D - K, H - C,
                A - E, B - F, J - D, I - C,
                0, 0, 0, 0
            )

    def __init__(self, A, B, C, D, E, F, G, H, I, J, K, L):
        """
        These are the vectors used to define a Tile. The u direction is from A to B,
        the v direction is from A to D.

                    u --->

                    E   F
                    |   |
            v   L---A---B---G
                    |   |
            |   K---D---C---H
            |       |   |
            V       J   I
        """
        self.xlayer = self.Layer.from_vectors(
            A, B, C, D, E, F, G, H, I, J, K, L,
            lambda vector: vector[0]
        )
        self.ylayer = self.Layer.from_vectors(
            A, B, C, D, E, F, G, H, I, J, K, L,
            lambda vector: vector[1]
        )
        self.zlayer = self.Layer.from_vectors(
            A, B, C, D, E, F, G, H, I, J, K, L,
            lambda vector: vector[2]
        )

    def __call__(self, u, v):
        return Vector([
            self.xlayer(u, v),
            self.ylayer(u, v),
            self.zlayer(u, v)
        ])

    def to_gnuplot(self, fnfmt, ribs=10):
        def rotated(u, v, r=Matrix.rotate_x(5)*Matrix.rotate_z(15)):
            h = Vector(0.5, 0.5, 0.5)
            return r * (self(u, v) - h) + h

        assert "{0}" in fnfmt, fnfmt
        filenames = []
        for j in xrange(0, ribs):
            v = 1. * j / (ribs - 1)
            fn = fnfmt.format(j)
            filenames.append(fn)
            outf = open(fn, 'w')
            fn2 = fnfmt.format(j + ribs)
            filenames.append(fn2)
            outf2 = open(fn2, 'w')
            n = 100
            for i in xrange(0, n + 1):
                u = 1. * i / n
                outf.write("{0} {1}\n".format(
                    rotated(u, v)[0],
                    rotated(u, v)[2]
                ))
                outf2.write("{0} {1}\n".format(
                    rotated(v, u)[0],
                    rotated(v, u)[2]
                ))
            outf.close()
            outf2.close()
        return filenames


def try_tile():
    # python -c 'import splines; splines.try_tile()'
    t = Tile(
        Vector(0, 0, 0), Vector(1, 0, 0), Vector(1, 1, 0), Vector(0, 1, 0),
        Vector(0, -1, -1), Vector(1, -1, -1),
        Vector(2, 0, -1), Vector(2, 1, -1),
        Vector(1, 2, -1), Vector(0, 2, -1),
        Vector(-1, 1, -1), Vector(-1, 0, -1)
    )
    fnfmt = "tile{0}.dat"
    ribs = 12
    fns = t.to_gnuplot(fnfmt, ribs)
    outf = open("gp.cmd", "w")
    outf.write(
        'plot ' +
        ', '.join(['"{0}" with lines notitle'.format(fn) for fn in fns]) +
        '; pause 10;'
    )
    outf.close()
    os.system("gnuplot gp.cmd")
    for f in (["gp.cmd"] + fns):
        os.remove(f)


if __name__ == '__main__':
    nose.main(argv=["--verbosity=3", os.path.abspath(__file__)])
