import inspect
import pdb
import re
import os
import sys
import pprint
from jinja2 import Template, Environment, BaseLoader


DEBUG = False


class Finder(object):
    def __init__(self):
        self.continuation = None
        self.things = []
        self.prev_preamble = None

    def start(self, line):
        return None, None    # preamble, stuff to save

    def middle(self, line):
        return None, None    # preamble, stuff to save

    def end(self, line):
        return None, None    # preamble, stuff to save

    def process_line(self, line):
        if self.continuation is None:
            assert self.prev_preamble is None
            preamble, stuff = self.start(line)
            if stuff is not None:
                self.prev_preamble = preamble
                self.continuation = stuff
        do other stuff....



def render(target):
    f = inspect.currentframe(1)
    fi = os.path.realpath(f.f_globals['__file__'])
    g = f.f_globals
    R = map(lambda x: x.rstrip(),
            open(fi).readlines())
    comments = []
    last_start = None
    continuation = None
    for line in R:
        if DEBUG: print 'LINE', line
        m = re.match(r"^(\s*)#\s*(.*)", line, flags=re.MULTILINE)
        if m is None:
            if DEBUG: print "A", line
            if continuation is not None:
                # end of comment, save it in array
                comments.append(continuation)
                if DEBUG: pprint.pprint(("A", comments))
                continuation = last_start = None
        elif continuation is None:
            # start of comment
            last_start = m.group(1)
            continuation = m.group(2)
            if DEBUG: print "E", m.groups(), continuation
        elif last_start == m.group(1):
            continuation += "\n" + m.group(2)
            if DEBUG: print "B", m.groups(), continuation
        else:
            print "D", m.groups(), continuation
            # change of indentation, end current comment, start new one
            comments.append(continuation)
            last_start = m.group(1)
            continuation = m.group(2)

    def comment_regex(key):
        if DEBUG: print 'KEY', key
        r = re.compile(key)
        for c in comments:
            if DEBUG: print 'C', c
            if r.search(c) is not None:
                lines = c.split('\n')
                lines = ['> ' + L for L in lines]
                return '\n'.join(lines)
        return ''

    def pretty_doc(thing):
        d = getattr(thing, '__doc__', None)
        if d is None:
            return ''
        return '## ' + thing.__name__ + '\n\n' + d

    def render_str(s):
        env = Environment(loader=BaseLoader)
        env.filters["cre"] = comment_regex
        tm = env.from_string(s)
        d = {
            thing.__name__: pretty_doc(thing)
            for thing in [v for v in g.values()
                          if callable(v) and hasattr(v, '__name__')]
        }
        if DEBUG: print 'dct', d
        return tm.render(**d)

    def render_obj(obj):
        if isinstance(obj, (str, unicode)):
            return render_str(obj)
        assert isinstance(obj, (list, tuple)), obj
        return "".join([render_obj(x) for x in obj])

    assert g.has_key(target), pprint.pformat((g, target))
    return render_obj(g[target])
