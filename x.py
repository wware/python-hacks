import re
from timetravel import time_travel


def inner(u, v):
    u *= 2
    # assert u == 5
    v *= 2
    return u + v


@time_travel()
def f(x):
    r = re.compile("^(.*)#(.*)$")
    x += 1
    y = r.search("abc#def")
    a, b = y.groups()
    print a, b
    return inner(x, 2)


print f(3)
