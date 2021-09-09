import inspect
import pdb
import re
import os
import sys
import pprint
import logging
from jinja2 import Template, Environment, BaseLoader


_FORMAT = "%(asctime)-15s  %(name)s:%(levelname)s  %(filename)s:%(lineno)d  %(message)s"
logger = logging.getLogger("litprog")
h = logging.StreamHandler(sys.stderr)
h.setFormatter(logging.Formatter(_FORMAT))
logger.addHandler(h)
logger.setLevel(logging.INFO)


def make_process_comments():
    comments = []
    state = [
        None,    # continuation
        None     # previous group 1
    ]

    def process_line(line):
        m = re.match(r"^(\s*#)\s(.*)", line, flags=re.MULTILINE)
        if m is not None:
            if state[0] is None:
                # start of comment
                state[0] = m.group(2)
                state[1] = m.group(1)
            else:
                if state[1] != m.group(1):
                    # indentation has changed, it's a new comment
                    comments.append(state[0])   # save the old comment
                    state[0] = m.group(2)
                    state[1] = m.group(1)
                else:
                    state[0] += '\n' + m.group(2)
        else:
            if state[0] is not None:
                # end of comment, save it
                comments.append(state[0])
                state[0] = state[1] = None

    return process_line, comments


def make_process_strings():
    strings = []
    state = [
        None,    # None=waiting_or_getting, 1=start_next_line
        None     # continuation
    ]

    def process_line(line):
        m = re.match(r'^(\'\'\'|""")', line)
        if m is not None:
            if state[0] is None:
                # the NEXT line is start of string
                state[0] = 1
                state[1] = ""
            else:
                # end of line
                strings.append(state[1].lstrip())
                state[0] = state[1] = None
        else:
            if state[1] is not None:
                state[1] += "\n" + line
            else:
                # start of string
                state[1] = line
                state[0] = None

    return process_line, strings


def render(target):
    f = inspect.currentframe(1)
    fi = os.path.realpath(f.f_globals['__file__'])
    g = f.f_globals
    R = map(lambda x: x.rstrip(),
            open(fi).readlines())
    process_line, comments = make_process_comments()
    process_line_2, strings = make_process_strings()
    for line in R:
        logger.debug(line)
        process_line(line)
        process_line_2(line)

    logger.debug(pprint.pformat(strings))

    def comment_regex(key):
        r = re.compile(key)
        for c in comments:
            if r.search(c) is not None:
                lines = c.split('\n')
                lines = ['> ' + L for L in lines]
                return '\n'.join(lines)
        return ''

    def strings_regex(key):
        r = re.compile(key)
        for s in strings:
            if r.search(s) is not None:
                return s
        return ''

    def pretty_doc(thing):
        d = getattr(thing, '__doc__', None)
        if d is None:
            return ''
        return '## ' + thing.__name__ + '\n\n' + d

    def render_str(s):
        env = Environment(loader=BaseLoader)
        env.filters["cre"] = comment_regex
        env.filters["sre"] = strings_regex
        tm = env.from_string(s)
        d = {
            thing.__name__: pretty_doc(thing)
            for thing in [v for v in g.values()
                          if callable(v) and hasattr(v, '__name__')]
        }
        logger.debug(d)
        return tm.render(**d)

    def render_obj(obj):
        if isinstance(obj, (str, unicode)):
            return render_str(obj)
        assert isinstance(obj, (list, tuple)), obj
        return "".join([render_obj(x) for x in obj])

    assert g.has_key(target), pprint.pformat((g, target))
    return render_obj(g[target])
