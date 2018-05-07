var assert = require('assert');
var linalg = require('../linalg.js');
var Vector = linalg.Vector;
var Matrix = linalg.Matrix;

describe('Vector', function() {
    describe('#negate()', function() {
        it('should work right', function() {
            assert.ok(Vector(1, 9, 16).negate().equals(Vector(-1, -9, -16)));
        });
    });
    describe('#add()', function() {
        it('should work right', function() {
            assert.ok(Vector(1, 9, 16).add(Vector(3, 4, 5)).equals(Vector(4, 13, 21)));
        });
    });
    describe('#subtract()', function() {
        it('should work right', function() {
            assert.ok(Vector(1, 9, 16).subtract(Vector(3, 4, 5)).equals(Vector(-2, 5, 11)));
        });
    });
});

var m1 = Matrix([1, 0, 0, 0, 2, 0], 2, 3);
var m2 = Matrix([3, 4, 5, 6, 7, 8], 2, 3);
var m3 = Matrix([3, 4, 5, 6, 7, 8], 3, 2);

describe('Matrix', function() {
    describe('#negate()', function() {
        it('should work right', function() {
            assert.ok(m1.negate().equals(Matrix([-1, 0, 0, 0, -2, 0], 2, 3)));
        });
    });
    describe('#add()', function() {
        it('should work right', function() {
            assert.ok(m1.add(m2).equals(Matrix([4, 4, 5, 6, 9, 8], 2, 3)));
        });
    });
    describe('#subtract()', function() {
        it('should work right', function() {
            assert.ok(m1.subtract(m2).equals(Matrix([-2, -4, -5, -6, -5, -8], 2, 3)));
        });
    });
    describe('#multiply()', function() {
        it('should work right', function() {
            assert.ok(m2.multiply(m3).equals(Matrix([64, 76, 109, 130], 2, 2)));
        });
    });
});
