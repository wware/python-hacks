# tinker with functional programming and
# immutable values and classes
# methods should be written in FP style

from collections import namedtuple

class Vector(namedtuple("V", "x y z")):
    def len(self):
        return self.inner(self) ** .5

    def inner(self, w):
        assert isinstance(w, Vector)
        return self.x*w.x + self.y*w.y + self.z*w.z

    def scale(self, k):
        return Vector(k*self.x, k*self.y, k*self.z)
