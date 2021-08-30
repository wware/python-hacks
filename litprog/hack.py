#!/usr/bin/python

"""
Meaningless docstring
"""

import argparse
import os
import litprog

"""
## Diverging from Knuth

Knuth's writings on Literate Programming describe a source document of a
novel format that is processed separately to produce source code in one
instance and a printable document for publication in the other. This is
burdensome since his novel format is not handled well by any tools. There
are far too many advantages to using source code as the format from which
to work. One is tooling, the other is removing the need to maintain a
novel format that nobody else uses, and finally, we remove an entire
toolchain by producing source code directly.

In the current aproach, we instead add machinery so that source code can
include elements that can be used to create the printable document. This
source file is an exploration of what that might look like, and how to
make it as flexible and useful as possible without being confusing.

To generate the printable document from this file, type

    PROG --target my_doc > README.md

We will follow the common pattern of keeping the additional docs in the
source code to prevent divergence.

Let's be able to refer to a function inside the doc text:

{{ parse_cmd_line_args }}
""".replace("PROG", "./" + os.path.basename(__file__))


def parse_cmd_line_args():
    """
    Here is my arg parser.
    :return: parsed args, DUH
    """
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        '-t', '--target',
        help='specify a target to render',
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='turn on debug-level debugging output',
    )
    parser.add_argument('extras', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.debug:
        litprog.DEBUG = True
    return args, args.extras


"""
## *Second* paragraph

Think about how this stuff could dovetail with the MTSL project.
Can we embed RDF into this somehow? And ideally in a way that it
could be automatically extracted and handed to a reasoner?

{{ "comment" | cre }}

and let's note a separate comment, differentiated by a change of
indentation

{{ "separate" | cre }}
"""

my_doc = """
# This is my markdown document

{{ "" | sre }}
{{ "" | sre }}
"""


# Let's put in a comment that we can refer to using a regular
# expression, and make it a multi-line comment so that we can
# pull complex thoughts out in that way. In Markdown these should
# be rendered as block quotes. Write a Jinja custom filter for this.
    # this should be a separate comment from
    # the one immediately above it

def main():
    options, extra_args = parse_cmd_line_args()
    # put this if clause in a decorator maybe?
    if options.target:
        print(litprog.render(options.target))
    else:
        # vanilla functionality, rather than litprog stuff
        print 1 + 2 + 3 + 4


if __name__ == '__main__':
    main()
