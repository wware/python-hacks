var assert = require("assert");

function map(fn, lst1, lst2) {
    var olst = [];
    for (var i = 0; i < lst1.length && (lst2 === undefined || i < lst2.length); i++) {
        olst.push(fn(lst1[i], (lst2 === undefined) ? undefined : lst2[i]));
    }
    return olst;
}

function sum(lst) {
    var _sum = 0;
    for (var i = 0; i < lst.length; i++) {
        _sum += lst1[i];
    }
    return _sum;
}


var vectorPrototype = {
    _toString: function() {
        return "(" + this.x + " " + this.y + " " + this.z + ")";
    },
    copy: function(other) {
        return Vector(this.x, this.y, this.z);
    },
    add: function(other) {
        return Vector(this.x + other.x,
                      this.y + other.y,
                      this.z + other.z);
    },
    subtract: function(other) {
        return Vector(this.x - other.x,
                      this.y - other.y,
                      this.z - other.z);
    },
    negate: function() {
        return Vector(-this.x, -this.y, -this.z);
    },
    scale: function(factor) {
        return Vector(this.x * factor,
                      this.y * factor,
                      this.z * factor);
    },
    normalize: function(factor) {
        return this.scale(1.0 / this.length());
    },
    dotProduct: function(other) {
        return this.x * other.x +
        this.y * other.y +
        this.z * other.z;
    },
    crossProduct: function(other) {
        return Vector(this.y * other.z - other.y * this.z,
                      this.z * other.x - other.z * this.x,
                      this.x * other.y - other.x * this.y);
    },
    equals: function(other) {
        return this.distsq(other) < 1.0e-20;
    },
    distsq: function(other) {
        var dx = this.x - other.x;
        var dy = this.y - other.y;
        var dz = this.z - other.z;
        return dx * dx + dy * dy + dz * dz;
    },
    lensq: function() {
        var x = this.x;
        var y = this.y;
        var z = this.z;
        return x * x + y * y + z * z;
    },
    length: function() {
        return Math.sqrt(this.lensq());
    }
};

function vectorConstructor() { }
vectorConstructor.prototype = vectorPrototype;

function Vector(x,y,z) {
    inst = new vectorConstructor();
    inst.x = x;
    inst.y = y;
    inst.z = z;
    inst._type = 'Vector';
    return inst;
}


var matrixPrototype = {
    add: function(other) {
        assert.equal(this.rows, other.rows);
        assert.equal(this.cols, other.cols);
        return Matrix(map(
            function(x, y) { return x + y },
            this.entries,
            other.entries
        ), this.rows, this.cols);
    },
    subtract: function(other) {
        assert.equal(this.rows, other.rows);
        assert.equal(this.cols, other.cols);
        return Matrix(map(
            function(x, y) { return x - y },
            this.entries,
            other.entries
        ), this.rows, this.cols);
    },
    negate: function() {
        return Matrix(map(
            function(x) { return -x },
            this.entries
        ), this.rows, this.cols);
    },
    equals: function(other) {
        var diff = this.subtract(other);
        var delta = 0;
        for (var i = 0; i < this.rows * this.cols; i++)
            delta += diff.entries[i] ** 2;
        return delta < 1.e-20;
    },
    multiply: function(other) {
        if (other._type == 'Matrix') {
            assert.equal(this.cols, other.rows);
            var lst = [];
            for (var row = 0; row < other.cols; row++)
                for (var col = 0; col < other.cols; col++) {
                    var _sum = 0;
                    for (var k = 0; k < this.cols; k++)
                        _sum += this.entries[k + this.cols * row] * other.entries[col + other.cols * k];
                    lst.push(_sum);
                }
            return Matrix(lst, this.rows, other.cols);
        }
        else if (other._type == 'Vector') {
            assert.equal(this.cols, other.length());
            assert.equal(this.cols, 3);
            var lst = [];
            for (var col = 0; col < 3; col++) {
                var _sum = 0;
                for (var row = 0; row < other.cols; row++) {
                    var other_entry =
                        (col == 0) ? other.x : ((col == 1) ? other.y : other.z);
                    _sum += this.entries[this.cols * row + col] * other_entry;
                }
                lst.push(_sum);
            }
            return Vector(lst[0], lst[1], lst[2]);
        }
        else {
            return Matrix(
                map(function (x) {return other * x}, this.entries),
                this.rows,
                this.cols
            );
        }
    }
};

function matrixConstructor() { }
matrixConstructor.prototype = matrixPrototype;

function Matrix(entries, rows, cols) {
    inst = new matrixConstructor();
    inst.entries = entries;
    inst.rows = rows;
    inst.cols = cols;
    inst._type = 'Matrix';
    return inst;
}

module.exports = {
    Vector: Vector,
    Matrix: Matrix
}









/*


class Vector(list):
    def __init__(self, *params):
        if len(params) > 1:
            list.__init__(self, params)
        else:
            list.__init__(self, *params)

    def __add__(self, other):
        return apply(self.__class__, [x + y for x, y in zip(self, other)])

    def __sub__(self, other):
        return apply(self.__class__, [x - y for x, y in zip(self, other)])

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


*/
