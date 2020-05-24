import types
from functools import wraps


def main(G):
    e = G.get("elsewhere")
    old_method = e.MyClass.mymethod

    @wraps(old_method)
    def my_new_method(self, x, y):
        print "x={0} y={1}".format(x, y)
        z = old_method(self, x, y)
        print "return {0}".format(z)
        return z

    e.MyClass.mymethod = my_new_method
