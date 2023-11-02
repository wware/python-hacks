#! /usr/bin/env python3

"""PROGRAM

This program extracts code from a Markdown document."""

EXAMPLE_USAGE = """# A simple python example

## *inner function*

I know this is a chunk that should be included in processing because
the section title is in italics (a "*" character in Markdown source).

This function will later be called by the `_outer` function below.

```python
def _inner(x):
    print(x)
```

When we import a code chunk with indentation, that indentation is
applied to the imported chunk. Adding a little more to the `_inner`
function to demonstrate this:

```python
    #*inner inner function*#
    pr_square(5)
    print("Have a good day")
```

## *inner inner function*

```python
def pr_square(x):
    print(x**2)
```

## this is not a chunk

We can throw in examples that aren't chunks and they don't get
processed in any way.

```python
def pr_cube(x):
    print(x**3)
```

## *outer function*

```python
#*inner function*#

def _outer(x):
    _inner(x)

_outer("Hello world")
```"""

import os
import sys
import re
import logging
import pprint
import argparse
from typing import List, Dict, TextIO


REFERENCE = r"^(\s*)#\*(.*)\*#"
CHUNK_NAME = r"^#{2,3}[ \t]+\*(.*)\*$"
CHUNK_DONE = r"^#{2,3}[ \t]+[^*].*"
CHUNK_DELIMITER = r"^```(\w*)"

logger = logging.getLogger("mdweb")
h = logging.StreamHandler()
_FORMAT = "%(asctime)-15s  %(filename)s:%(lineno)d  %(message)s"
h.setFormatter(logging.Formatter(_FORMAT))
logger.handlers = [h]


def main():
    lines: List[str] = []
    chunks: Dict[str,List[str]] = {}

    def read_source():
        chunkName = pendingChunkName = None
        for line in lines:
            match = re.match(CHUNK_NAME, line)
            if match:
                logger.debug(match)
                chunkName = None
                pendingChunkName = match.group(1)
                continue
            match = re.match(CHUNK_DONE, line)
            if match:
                logger.debug(match)
                pendingChunkName = None
                continue
            match = re.match(CHUNK_DELIMITER, line)
            if match:
                # logger.debug(match)
                if pendingChunkName and not chunkName:
                    chunkName = pendingChunkName
                    if chunkName not in chunks:
                        chunks[chunkName] = []
                else:
                    chunkName = None
                continue
            if chunkName:
                chunks[chunkName].append(line)

    def expand(chunk: str, indent: str) -> List[str]:
        chunkLines = chunks[chunk]
        expandedChunkLines = []
        for line in chunkLines:
            match = re.match(REFERENCE, line)
            if match:
                more_indent = match.group(1)
                expandedChunkLines.extend(expand(
                    match.group(2),
                    indent + more_indent
                ))
            else:
                expandedChunkLines.append(indent + line)
        return expandedChunkLines

    class ArgParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write(message + '\n')
            self.print_help()
            sys.exit(1)

    parser = ArgParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__.replace("PROGRAM", sys.argv[0])
    )
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='debug level logging',
    )
    parser.add_argument(
        '--example', '-X',
        action='store_true',
        help='show example usage',
    )
    parser.add_argument(
        '--ref', '-R',
        help='the root chunk to be extracted',
    )
    parser.add_argument(
        '--out', '-o',
        help='specify an output file',
    )
    parser.add_argument(
        '--executable', '-x',
        action='store_true',
        help='if an output file was specified, chmod +x that file',
    )
    parser.add_argument(
        'filename', nargs='*',
        help='the source file(s) from which to extract',
    )
    opts = parser.parse_args()
    if opts.example:
        print(EXAMPLE_USAGE)
        sys.exit(0)
    if not opts.filename:
        parser.error("Need an input filename")
    if opts.debug:
        logger.setLevel(logging.DEBUG)

    outfile: TextIO = sys.stdout
    if opts.out:
        outfile = open(opts.out, 'w')

    lines = [
        line.rstrip()
        for filename in opts.filename
        for line in open(filename).readlines()
    ]
    read_source()
    keys = list(chunks.keys())
    keys.sort()
    if not keys:
        parser.error('No references found in source file(s)')
    if not opts.ref:
        keys = '\n'.join((f"    {k}" for k in keys))
        parser.error(f'No root chunk specified, try one of these:\n{keys}')

    for line in expand(opts.ref, ""):
        print(line, file=outfile)

    if opts.out and opts.executable:
        os.system("chmod ugo+x " + opts.out)


if __name__ == '__main__':
    main()
