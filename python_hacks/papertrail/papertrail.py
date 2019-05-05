import types
import inspect
from collections import defaultdict


def get_stack(offset=0):
    def frame2tuple(frame):
        info = inspect.getframeinfo(frame[0])
        return (info.filename, info.lineno)
    return [frame2tuple(frame) for frame in inspect.stack()[offset+1:]]


def PaperTrail(cls):
    class newcls(cls):
        def __init__(self, *args, **kwargs):
            cls.__init__(self, *args, **kwargs)
            self.__method_calls = defaultdict(list)

        def __where__(self):
            return [self.__bt_at_init, get_stack(1)]

        def __add_call__(self, methodname, x):
            self.__method_calls[methodname].append(tuple(x))

        def __calls__(self):
            return dict(self.__method_calls)

    def __new_init__(self, *args, **kwargs):
        cls.__init__(self, *args, **kwargs)
        # pylint: disable=protected-access
        self._newcls__bt_at_init = get_stack(1)
        # pylint: enable=protected-access

    setattr(
        newcls,
        "__init__",
        types.MethodType(__new_init__, None, newcls)
    )

    # use __add_call__ to maintain record of method calls
    def method_renovator(methodname, method):
        def newmethod(self, *args, **kwargs):
            x = [get_stack(1), args, kwargs]
            r = method(self, *args, **kwargs)
            x.append(r)
            self.__add_call__(methodname, x)
            return r
        return newmethod

    # wrap all the non-dunder methods with renovator
    for methodname in (x for x in dir(cls) if not x.startswith("__")):
        method = getattr(cls, methodname)
        if callable(method):
            method = types.MethodType(
                method_renovator(methodname, method), None, newcls)
        setattr(newcls, methodname, method)
    return newcls


@PaperTrail
class DataThingy(object):
    def __init__(self, x):
        self._x = x

    def x(self, *_):
        return self._x


if __name__ == "__main__":
    # pylint: disable=protected-access,no-member
    thingy = DataThingy(3)                 # line 63
    assert thingy._x == 3
    assert thingy.x('a', 'b', 1234) == 3   # line 65
    got = thingy.__where__()               # line 66
    expected = [
        [('papertrail.py', 63)],
        [('papertrail.py', 66)]
    ]
    assert got == expected, (got, expected)
    assert thingy.__calls__() == {
        'x': [(
            [('papertrail.py', 65)],  # where x() was called
            ('a', 'b', 1234),         # args
            {},                       # kwargs
            3
        )]                            # return value
    }, thingy.__calls__()
    # pylint: enable=protected-access,no-member
