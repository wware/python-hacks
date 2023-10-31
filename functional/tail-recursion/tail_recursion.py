class recurse:
    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw


def tail_recursive(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kw):
        while True:
            res = f(*args, **kw)
            if isinstance(res, recurse):
                args = res.args
                kw = res.kw
            else:
                return res
    return wrapper
