#!/usr/bin/env python

import argparse
import logging
import os
import sys
import pprint
from textwrap import dedent

HERE = os.path.dirname(__file__)
__doc__ = open(os.path.join(HERE, 'argparse_example.md')).read()

logging.getLogger().setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='turn on debug-level logging',
    )
    opts = parser.parse_args(sys.argv[1:])
    if opts.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    pprint.pprint(opts.__dict__)


if __name__ == '__main__':
    main()
