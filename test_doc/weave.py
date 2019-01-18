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


def hack_file_2(src, verbose=False):
    re1 = re.compile(r"#\+([_a-zA-Z][_\-0-9a-zA-Z]+)")
    re2 = re.compile(r"#-([_a-zA-Z][_\-0-9a-zA-Z]+)")

    start = {}
    finish = {}

    for i, line in enumerate(src.split("\n")):
        line = line.strip()
        m = re1.search(line)
        if m is not None:
            target = m.group(1)
            start[target] = i + 1
        m = re2.search(line)
        if m is not None:
            target = m.group(1)
            finish[target] = i + 1

    keys = set(start.keys()).intersection(finish.keys())
    return {k: (start[k], finish[k]) for k in keys}


doclines = sys.stdin.readlines()
rdoc1 = re.compile(r"^@([_a-zA-Z][_0-9a-zA-Z]+.py):([_a-zA-Z][._0-9a-zA-Z]+)")
rdoc2 = re.compile(r"^=([_a-zA-Z][_0-9a-zA-Z]+.py):([_a-zA-Z][_\-0-9a-zA-Z]+)")
lookups = {}

for line in doclines:
    line = line.rstrip()
    m = rdoc1.search(line)
    if m is not None:
        filename = m.group(1)   #+hack-regex-1
        dotted = m.group(2)
        if filename not in lookups:
            lookups[filename] = hack_file(open(filename).read())
        assert dotted in lookups[filename], "Cannot find {0}:{1}".format(filename, dotted)  #-hack-regex-1
    m = rdoc2.search(line)
    if m is not None:
        filename = m.group(1)
        target = m.group(2)
        d = hack_file_2(open(filename).read())
        if filename not in lookups:
            lookups[filename] = d
        else:
            lookups[filename].update(d)
        assert target in lookups[filename], "Cannot find {0}:{1}".format(filename, target)

if '-hack' in sys.argv[1:]:
    import pprint
    pprint.pprint(lookups)
    sys.exit(0)

result = []
for line in doclines:
    line = line.rstrip()
    m = rdoc1.search(line)
    if m is not None:
        filename = m.group(1)   #+hack-regex-2
        dotted = m.group(2)
        lines = [l.rstrip() for l in open(filename).readlines()]
        m, n = lookups[filename][dotted]
        for l in lines[m-1:n]:
            result.append('    ' + l)  #-hack-regex-2
    else:
        m = rdoc2.search(line)
        if m is not None:
            filename = m.group(1)
            target = m.group(2)
            lines = [l.rstrip() for l in open(filename).readlines()]
            m, n = lookups[filename][target]
            these_lines = lines[m-1:n]
            result.append('    ' + re.sub(r"\s+#\+{0}\s*$".format(target), "", these_lines[0]))
            for l in these_lines[1:-1]:
                result.append('    ' + l)
            result.append('    ' + re.sub(r"\s+#-{0}\s*$".format(target), "", these_lines[-1]))
        else:
            result.append(line)

print '<html>' + markdown.markdown('\n'.join(result)) + '</html>'
