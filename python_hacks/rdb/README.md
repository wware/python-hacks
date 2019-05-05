Remote debugging
====

Adds a few helpful things to the `remote-pdb` module. You can set it up
to email you when it enters the debugger, and once in the debugger, you
can run shell commands.

Pip install
----

```
$ virtualenv venv; source venv/bin/activate
New python executable in venv/bin/python
Installing setuptools, pip...done.
(venv)$ pip install git+ssh://git@github.com/wware/rdb.git
```

Example usage
----

```python
from rdb import RemotePdb

def tryit():
RemotePdb(
    smtp_server='mail.veracode.local',
    sender='wware@alum.mit.edu',
    recipients=['wware@alum.mit.edu']
).set_trace()

def add(u, v):
    return u + v

x = 3
y = 4
print add(x, y)
```

A debugging session, including some shell commands
----

```
$ telnet localhost 4444
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
--Return--
> /home/wware/rdb/rdb/__init__.py(55)set_trace()->None
-> remote_pdb.RemotePdb.set_trace(self)
(Pdb) l
 50
 51         def set_trace(self):
 52             if self._notifier:
 53                 self._notifier._port = self._port
 54                 self._notifier.start()
 55  ->         remote_pdb.RemotePdb.set_trace(self)
 56
 57         # Be able to run shell commands
 58         def do_sh(self, *args):
 59             cmd = ' '.join(args)
 60             print >>self.stdout, os.popen(cmd).read().rstrip()
(Pdb) sh pwd
/home/wware/tmp2
(Pdb) sh ls -al
total 16
drwxrwxr-x   3 wware wware 4096 Apr  8 12:14 .
drwxr-xr-x 100 wware wware 4096 Apr  8 12:03 ..
-rw-rw-r--   1 wware wware  340 Apr  8 12:08 local_test.py
drwxrwxr-x   6 wware wware 4096 Apr  8 12:14 venv
(Pdb) c
Connection closed by foreign host.
```

Distributed logging
====

TODO: document this, for now look at test_dlog.py
