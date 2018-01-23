#!/usr/bin/env python

"""
Plugh
"""

import argparse
import logging
import os
import subprocess
import sys
import pprint
from textwrap import dedent

HERE = os.path.dirname(__file__)
myname = os.path.basename(__file__)

logging.getLogger().setLevel(logging.INFO)

pyfiles = []
rootDir = '.'
for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
        if fname.endswith(".py"):
            fname = '%s/%s' % (dirName, fname)
            fname = fname[len(rootDir)+1:]
            if fname != myname:
                pyfiles.append(fname)


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='check all files, ignoring failures',
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='turn on debug-level logging',
    )
    parser.add_argument(
        '-f', '--files',
        nargs='*',
        choices=pyfiles,
        help='which tests to run',
    )
    all_stages = ['flake8', 'pylint', 'tests']
    parser.add_argument(
        '-s', '--stages',
        nargs='*',
        choices=all_stages,
        help='which stages to run',
    )
    opts = parser.parse_args(sys.argv[1:])
    if opts.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    if not opts.files:
        opts.files = pyfiles
    if not opts.stages:
        opts.stages = all_stages
    logging.debug(pprint.pformat(opts.__dict__))

    if 'flake8' in opts.stages:
        for f in opts.files:
            try:
                subprocess.check_call(["flake8", f])
            except subprocess.CalledProcessError:
                if not opts.all:
                    raise
    if 'pylint' in opts.stages:
        for f in opts.files:
            try:
                subprocess.check_call(["pylint", f])
            except subprocess.CalledProcessError:
                if not opts.all:
                    raise
    if 'tests' in opts.stages:
        for f in opts.files:
            if "__init__.py" not in f:
                try:
                    subprocess.check_call(["nosetests", f])
                except subprocess.CalledProcessError:
                    if not opts.all:
                        raise

if __name__ == '__main__':
    main()
