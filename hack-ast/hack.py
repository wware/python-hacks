#!/usr/bin/env python

import ast
import pprint


def hack_file(src, verbose=False):
    d = {}

    def find_lines(obj, indent, stack):
        if stack is None:
            stack = []
        r = obj.lineno
        if verbose:
            _indent = (4 * indent) * " "
            print _indent, (
                obj.lineno,
                obj.name if hasattr(obj, 'name') else obj,
                stack
            )
        for b in getattr(obj, 'body', []):
            r = max(r, find_lines(
                b,
                indent + 1,
                stack + ([obj.name] if hasattr(obj, 'name') else [])
            ))
        if hasattr(obj, 'name'):
            dotted = '.'.join(stack + [obj.name])
            d[dotted] = (obj.lineno, r)
        return r

    x = ast.parse(src)
    for c in x.body:
        find_lines(c, 0, [])
    return d


def main():
    src = open(__file__).read()
    r = hack_file(src, verbose=True)
    pprint.pprint(r)


if __name__ == '__main__':
    main()
