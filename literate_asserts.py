# Kudos and gratitude to Paul Panzer for the second answer to
# https://stackoverflow.com/questions/42497625
import inspect
import sys

# when we don't actually want an exception raised
MESSAGE_ONLY = object()

def literate_assert(template):
    def check(cond, **kwargs):
        if cond is MESSAGE_ONLY or not cond:
            d = inspect.stack()[1][0].f_locals
            d.update(kwargs)
            s = template.format(**d)
            if cond is MESSAGE_ONLY:
                print(s)
            else:
                raise AssertionError(s)
    return check


A = literate_assert("""
Hey {name}, the errno is {errno}.
and we have object attributes like
foo.a = {foo.a}
foo.b = {foo.b}

A literate assert starts with a formatted string. Then you have
pre-conditions. Then functional code. Then post-conditions. The formatted
string can be detailed enough to explain the intent of the code, what is
known with certainty, what questions remain open, what actions still need
to be taken. The conditions should test whatever you need for the code to
be successful.
""")


# make sure formatting is really deferred, assign variables afterwards
class Foo(object):
    pass
foo = Foo()
foo.a = 123
foo.b = 456
name = "wware"
errno = 31415926

# now try the silly thing, add a cmd line arg to trigger the assert
precondition_failed = False
A(not precondition_failed)
print("Now we are doing exciting functional code stuff")
postcondition_failed = (len(sys.argv) > 1)
A(not postcondition_failed, errno=12345)
