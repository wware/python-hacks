X = object()   # indeterminate


def bw(u):
    if u is X:
        return X
    return 1 if u else 0


def bv(x, y, outcomes):
    def f(u):
        u = bw(u)
        return 2 if u is X else u
    return LVar(outcomes[f(x) + 3 * f(y)])


class LVar(object):
    def __init__(self, value=X):
        self.value = bw(value)
    def __or__(self, other):
        return bv(
            self.value, other.value,
            [0,1,X,1,1,1,X,1,X]
        )
    def __and__(self, other):
        return bv(
            self.value, other.value,
            [0,0,0,0,1,X,0,X,X]
        )
    def __invert__(self):
        return bv(
            self.value, 0,
            [1,0,X]
        )
    def __bool__(self):
        return not (not self.value)
    def __repr__(self):
        return ("X" if self.value is X
                     else repr(self.value))
    def __eq__(self, other):
        if not isinstance(other, LVar):
            return self.value == bw(other)
        return self.value == other.value
    @classmethod
    def enum(cls, n):
        u, v = (cls(0),), (cls(1),)
        if n == 1:
            return [u, v]
        x = cls.enum(n - 1)
        return [u + z for z in x] + [v+z for z in x]

    @classmethod
    def solve(cls, f):
        n = f.__code__.co_argcount
        satisfiable = False
        for args in LVar.enum(n):
            if f(*args):
                print(args)
                satisfiable = True
        if not satisfiable:
            print("Unsatisfiable")

def implies(u, v):
    return ~u | v

# ========================
# Application

def f(p, q, r):
    return all([
        # facts
        implies(p, q),
        ~q
        # what about rules?
    ])

LVar.solve(f)
