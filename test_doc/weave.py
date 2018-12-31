#!/usr/bin/env python

import importlib
import markdown
import os
import re
import sys
import tempfile
import time
import webbrowser


def hackDocstring(d):
    r = re.compile(r"^(\s*)([^\s].*)")
    n = None
    L = []
    for i, s in enumerate(d.split("\n")):
        m = r.match(s)
        if m is not None:
            if i > 0:
                n1 = len(m.group(1))
                n = n1 if n is None else min(n, n1)
            L.append(m.group(2))
        elif i > 0:
            L.append('')
    return (n, '\n'.join(L).rstrip())


t = importlib.import_module('tests')
n, s = hackDocstring(t.TestMyStuff.__doc__)
print n
print '<<<' + s + '>>>'
n, s = hackDocstring(t.TestMyStuff.test_add.__doc__)
print n
print '<<<' + s + '>>>'
