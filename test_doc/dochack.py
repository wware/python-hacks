#!/usr/bin/env python
"""
Here's an idea: documentation that can be tested - specifically, the
usage examples can be subjected to testing, to make sure that they
still correctly illustrate how the code works. So let's take a super
simple example. I'm documenting a function that adds two numbers.

    >>> add(4, 2)
    6
    >>> add(3.14159, 2.71828)
    5.85987

Now I can pull out this __doc__ string and include it in a larger
document like a PDF, or I can just leave it here for the next developer
(or me, in six months) to consult.

Python's doctest provides a nice approach to this, but it would be
good to allow more flexibility, maybe using unittest instead.
"""

import argparse
import os
import doctest


def add(x, y):
    return x + y


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
        try:
            import markdown, webbrowser
            filename = '/tmp/dochack.html'
            m = markdown.Markdown()
            outf = open(filename, 'w')
            outf.write('<html>')
            outf.write(m.convert(__doc__))
            outf.write('</html>')
            outf.close()
            webbrowser.open(filename)
            return
        except ImportError:
            print "You might need to 'pip install markdown Pygments'"

    finder = doctest.DocTestFinder(verbose=opts.verbose, recurse=False)
    runner = doctest.DocTestRunner(verbose=opts.verbose, optionflags=0)
    for test in finder.find(__doc__, name=__file__, globs=globals()):
        runner.run(test, compileflags=None)
    if (not opts.verbose and runner.failures == 0):
        print "ok"


if __name__ == "__main__":
    main()
