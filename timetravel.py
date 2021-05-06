import re
import os
import sys
import random
import json
from datetime import datetime, date, time as _time, timedelta
from functools import wraps


IGNORE = os.path.dirname(sys.argv[0])


HTML_TEMPLATE = """
<html>
<head>
    <link rel="stylesheet" href="https://code.jquery.com/ui/1.11.2/themes/smoothness/jquery-ui.css">
    <script src="https://code.jquery.com/jquery-latest.js"></script>
    <script src="https://code.jquery.com/ui/1.11.2/jquery-ui.js"></script>
    <script src="timetravel.js"></script>
    <style>
        div.scroll {
            height: 450px;
            overflow-y: auto;
        }
        .big {
            width: 200px;
            vertical-align: top;
        }
    </style>
    <script type='text/javascript'>
        window.onload = function() {
            $("button#far-left").click(far_left_click);
            $("button#left").click(left_click);
            $("button#right").click(right_click);
            $("button#far-right").click(far_right_click);
            $.ajax({
                url: 'JSONFILE',
                type: 'GET',
                cache: false,
                dataType: 'json'
            }).fail(function(e) {
                alert("Bad JSON file");
                console.log(e);
            }).done(function(data) {
                console.log("D");
                $.map(data.filenames, function(j) {
                    prepare_file(j);
                });
                data = data.data;
                steps = data;
                num_steps_to_process = data.length - 1;
            });
        }
    </script>
</head>
<body>
    <h1 id="filename"></h1>
    <div>
        <button id="far-left">&lt;&lt;&lt;</button>
        <button id="left">&lt;</button>
        <button id="right">&gt;</button>
        <button id="far-right">&gt;&gt;&gt;</button>
    </div>
    <div>
        <table>
            <tr>
                <td class="big">
                    <table>
                        <tr><td><div>
                            <div id="target" class="scroll">
                            </div>
                        </div></td></tr>
                    </table>
                </td>
                <td class="big">
                    <pre id="vars" class="scroll">
                    </pre>
                    <div id="returnvalue">
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
"""


def time_travel(htmlfile=None):
    LOGFILE = 'x.log'
    f_index = [0]
    forward = {}    # map filename to index
    fromframe = {}  # map id(frame) to index

    jsonfile = 'X{0:x}.json'.format(random.randint(1, 1<<32))
    if htmlfile is None:
        htmlfile = 'X{0:x}.html'.format(random.randint(1, 1<<32))
        print 'HTML file for time travel debug is {0}'.format(htmlfile)

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
        os.unlink(logfile)

    def fix_json_char(ch):
        # json.dumps barfs on ASCII codes outside vanilla EN-US range
        # and also on datetime.* types
        if 32 <= ord(ch) <= 126:
            return str(ch)
        else:
            return ' '

    def make_json_dumpable(obj):
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
    def decorator(f):
        outf = open(LOGFILE, 'w')

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
                make_json_file(LOGFILE, jsonfile)
                open(htmlfile, 'w').write(HTML_TEMPLATE.replace("JSONFILE", jsonfile))
        return wrapped
    return decorator
