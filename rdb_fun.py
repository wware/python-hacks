import os
import remote_pdb

r = remote_pdb.RemotePdb('0.0.0.0', 4444)

"""
I want a remote debugging session where I can periodically check whether a file
or directory still exists. So let's add a function "f" to the remote debugger.
"""

def f(*args):
    x = os.path.isfile('rdb_fun.py') and 'still exists' or 'is gone!'
    print >> r.stdout, 'rdb_fun.py ' + x

r.do_f = f
r.set_trace()

def fac(n):
    p = 1
    for i in range(2, n+1):
        p *= i
    return p

print fac(5)
