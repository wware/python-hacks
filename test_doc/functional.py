#!/usr/bin/env python
"""
Here's an idea: documentation that can be tested - specifically, the
usage examples can be subjected to testing, to make sure that they
still correctly illustrate how the code works. So let's take a super
simple example. I'm documenting a function that adds two numbers.

Now I can pull out this __doc__ string and include it in a larger
document like a PDF, or I can just leave it here for the next developer
(or me, in six months) to consult.

The more complete way to do this would be like literate programming
where you have one process for converting the source text into
human-readable documentation, and another process for testing the
examples.

In this unittest-based scheme, groups of code lines are translated
into methods in a TestCase class. Any line with a "!!" comment becomes
an `assertTrue` statement. Groups of lines are separated by blank lines
and each group is translated into one method in a TestCase class.

    add(4, 2) == 6      !! this is an assertion
    add(3, 19) == 22    !!

    f = Foo()
    isinstance(f, Foo)   !!
    f.add_five(3) == 8   !!

    # Use only single quotes in these strings
    tweak_line('a b') == 'a b'        !!
    'green' in tweak_line('a b !!')   !!
"""

import argparse
import cgi
import imp
import os
import re
import tempfile
import unittest


class Foo(object):
    def add_five(self, x):
        print 'do something useless here'
        return add(x, 5)


def add(x, y):
    return x + y


preamble = """import unittest
class TestMyStuff(unittest.TestCase):
"""

def tweak_line(line):
    line = cgi.escape(line)
    if '!!' in line:
        # TODO split off leading spaces, add <span> stuff, put them back
        line = '<span style="color: green;">' + line + '</span>'
    return line


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='turn on debug-level logging',
    )
    parser.add_argument(
        '-m', '--markdown',
        action='store_true',
        help='do Markdown HTML generation of docstring',
    )
    opts = parser.parse_args()

    if opts.markdown:
        # it would be better to do this line-by-line as we do below,
        # so we can handle cases more gracefully, maybe convert the
        # assertions to a different color.
        doc = '\n'.join([tweak_line(line) for line in __doc__.split("\n")])
        print doc

        import time, markdown, webbrowser
        outf = tempfile.NamedTemporaryFile(delete=False)
        filename = outf.name
        m = markdown.Markdown()
        outf.write('<html>')
        outf.write(m.convert(doc))
        outf.write('</html>')
        outf.close()
        webbrowser.open(filename)
        time.sleep(3)
        os.unlink(filename)
        return

    groups = []
    group = []
    for line in __doc__.split("\n"):
        if line.startswith("    ") and not line.startswith("    #"):
            L = line[4:]
            assertion = False
            if '!!' in line:
                n = L.rindex('!!')
                assertion = True
                L = L[:n].rstrip()
            if assertion:
                group.append("self.assertTrue(" + L + ", \"" + L + "\")")
            else:
                group.append(L)
        else:
            if group:
                groups.append(group)
                group = []
    if group:
        groups.append(group)

    def test(n, group):
        r = "    def test_{0}(self):\n".format(n)
        for L in group:
            r += (8 * " ") + L + "\n"
        return r

    outf = tempfile.NamedTemporaryFile(delete=False)
    outf.write(preamble)
    if opts.verbose:
        print preamble
    tests = "\n".join([test(i, group) for i, group in enumerate(groups)])
    if opts.verbose:
        print tests
    outf.write(tests)
    outf.close()

    mystuff = imp.load_source("mystuff", outf.name)
    for key, value in globals().items():
        setattr(mystuff, key, value)

    suite = unittest.TestSuite()
    for method in dir(mystuff.TestMyStuff):
        if method.startswith("test"):
            suite.addTest(mystuff.TestMyStuff(method))
    runner = unittest.TextTestRunner(verbosity=(2 if opts.verbose else 0))
    x = runner.run(suite)
    if len(x.errors) + len(x.failures) == 0:
        os.unlink(outf.name)

if __name__ == "__main__":
    main()
