#!/usr/bin/env python

import ast
import markdown
import os
import re
import sys
import tempfile
import time
import webbrowser


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


doclines = sys.stdin.readlines()
rdoc = re.compile(r"^@([_a-zA-Z][_0-9a-zA-Z]+.py):([_a-zA-Z][._0-9a-zA-Z]+)")
lookups = {}

for line in doclines:
    line = line.rstrip()
    m = rdoc.search(line)
    if m is not None:
        filename = m.group(1)
        dotted = m.group(2)
        if filename not in lookups:
            lookups[filename] = hack_file(open(filename).read())
        assert dotted in lookups[filename], "Cannot find {0}:{1}".format(filename, dotted)

result = []
for line in doclines:
    line = line.rstrip()
    m = rdoc.search(line)
    if m is not None:
        filename = m.group(1)
        dotted = m.group(2)
        lines = [l.rstrip() for l in open(filename).readlines()]
        m, n = lookups[filename][dotted]
        for l in lines[m-1:n]:
            result.append('    ' + l)
    else:
        result.append(line)

print '<html>' + markdown.markdown('\n'.join(result)) + '</html>'
