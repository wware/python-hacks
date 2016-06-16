import types

def dig(obj, depth, _filter=None, callables=False):
    """
    Dig through an object to see its structure.
    """
    if _filter is None:
        _filter = lambda *args: True

    def skip_dunder(key):
        dunder = (
            (isinstance(key, str) or isinstance(key, unicode))
            and key.startswith('__')
        )
        return not dunder

    # pylint: disable=unidiomatic-typecheck
    if (obj is None or
            type(obj) in (
                types.BooleanType, types.IntType, types.LongType,
                types.FloatType, types.ComplexType,
                str, unicode
            ) or (
                (not callables) and
                type(obj) in (
                    types.FunctionType, types.MethodType,
                    types.BuiltinFunctionType, types.BuiltinMethodType,
                    types.LambdaType
                ))):
        return obj
    elif isinstance(obj, list) or isinstance(obj, tuple):
        keys = xrange(len(obj))
        selector = lambda k, obj=obj: obj[k]
    elif isinstance(obj, dict):
        keys = [key for key in obj.keys() if skip_dunder(key)]
        selector = lambda k, obj=obj: obj.get(k)
    else:
        keys = [key for key in dir(obj) if skip_dunder(key)]
        selector = lambda k, obj=obj: getattr(obj, k)

    # collect = {'__type': type(obj)}
    collect = {}
    if depth > 0:
        for k in keys:
            y = selector(k)
            if _filter(k, y):
                collect[k] = dig(y, depth - 1, _filter, callables)
    return collect
