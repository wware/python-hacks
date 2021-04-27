import re
import os
import sys
import json
from datetime import datetime, date, time as _time, timedelta
from functools import wraps


IGNORE = os.path.dirname(sys.argv[0])


def make_json_file(logfile, jsonfile):
    outf = open(jsonfile, 'w')
    outf.write('{"data":[')
    r = re.compile("^([^ ]+) ([^ ]+) ([^ ]+) ([^ ]+) (.*)")
    filenames = []
    mode = 0
    started = False
    for line in open(logfile).readlines():
        line = line.rstrip()
        if line == '====':
            mode = 1
            outf.write('],"filenames":')
        elif mode == 0:
            groups = r.match(line).groups()
            if groups[0] in ('call', 'line', 'return'):
                d = {
                    'F': groups[1],
                    'L': int(groups[2]),
                    'V': groups[4]
                }
                if groups[0] == 'return':
                    d['E'] = groups[0]
                    d['A'] = groups[3]
                if started:
                    outf.write(',')
                outf.write(json.dumps(d) + '\n')
                started = True
        else:
            filenames.append(line)
    outf.write(json.dumps(filenames) + '}')
    outf.close()


def decorator(f):
    f_index = [0]
    forward = {}    # map filename to index
    fromframe = {}  # map id(frame) to index

    LOGFILE = 'x.log'
    JSONFILE = 'x.json'
    outf = open(LOGFILE, 'w')

    def make_json_dumpable(obj):
        def fix_json_char(ch):
            # json.dumps barfs on ASCII codes outside vanilla EN-US range
            # and also on datetime.* types
            if 32 <= ord(ch) <= 126:
                return str(ch)
            else:
                return ' '
        if obj is None or isinstance(obj, (int, long, float)):
            return obj
        elif isinstance(obj, complex):
            return {'real': obj.real, 'imag': obj.imag}
        elif isinstance(obj, (str, unicode)):
            return ''.join((fix_json_char(x) for x in obj))
        elif isinstance(obj, (set, list, tuple)):
            return [make_json_dumpable(x) for x in obj]
        elif isinstance(obj, datetime) or isinstance(obj, date) or isinstance(obj, _time):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        elif isinstance(obj, (set, list, tuple)):
            return [make_json_dumpable(x) for x in obj]
        elif isinstance(obj, dict):
            return {
                make_json_dumpable(k):
                make_json_dumpable(v)
                for k, v in obj.items()
            }
        else:
            try:
                return repr(obj)
            except:
                return "???"

    def trace_func(frame, event, arg):
        filename = os.path.realpath(frame.f_code.co_filename)
        if filename.startswith("/usr"):
            return trace_func
        i = id(frame)
        fi = fromframe.get(i, None)
        if fi is None:
            # filename = os.path.realpath(frame.f_code.co_filename)
            filename = frame.f_code.co_filename.replace(IGNORE, "")
            fi = forward.get(filename, None)
            if fi is None:
                fi = f_index[0]
                f_index[0] += 1
                forward[filename] = fi
            fromframe[i] = fi
        outf.write(
            '{0} {1} {2} {3} '.format(event, fi, frame.f_lineno, arg) +
            json.dumps(make_json_dumpable(frame.f_locals)) +
            '\n'
        )
        if event == 'return':
            fromframe[i] = None
        return trace_func

    @wraps(f)
    def wrapped(*args, **kw):
        orig = sys.gettrace()
        try:
            sys.settrace(trace_func)
            return f(*args, **kw)
        finally:
            outf.write("====\n")
            items = [(v, k) for k, v in forward.items()]
            items.sort()
            for k, v in items:
                outf.write("{0}\n".format(v))
            outf.close()
            sys.settrace(orig)
            make_json_file(LOGFILE, JSONFILE)
    return wrapped


########################


def inner(u, v):
    u *= 2
    # assert u == 5
    v *= 2
    return u + v


@decorator
def f(x):
    import re
    r = re.compile("^(.*)#(.*)$")
    x += 1
    y = r.search("abc#def")
    a, b = y.groups()
    print a, b
    return inner(x, 2)


print f(3)
# print tr.stuff()

"""
The next thing is to make up a web page that presents a debugger-like
interface using this stuff. Let's do that in x.html.

So after this runs, run

    python -m SimpleHTTPServer

and then in your browser go to

    http://localhost:8000/x.html
"""
