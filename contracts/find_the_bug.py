# Use DbC to limit the search space for a bug.

import argparse
import logging
import sys

import contracts

opts = None
logging.getLogger().setLevel(logging.INFO)

@contracts.contract(returns='list[4](str)')
def first_part():
    if opts.first:
        return 'Something bogus this way comes.'
    return 'A,B,C,D'.split(',')

@contracts.contract(returns='list[4](str)')
def second_part():
    if opts.second:
        return 'Something bogus this way comes.'
    return 'E,F,G,H'.split(',')

@contracts.new_contract
def lowercase(x):
    return x == x.lower()

@contracts.contract(lst='list(str)', returns='list(str,lowercase)')
def tolowercase(lst):
    if opts.lowercase:
        return 'Something bogus this way comes.'
    return [s.lower() for s in lst]

def main():
    global opts
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='turn on debug-level logging',
    )
    parser.add_argument(
        '--first',
        action='store_true',
    )
    parser.add_argument(
        '--second',
        action='store_true',
    )
    parser.add_argument(
        '--lowercase',
        action='store_true',
    )
    opts = parser.parse_args(sys.argv[1:])
    if opts.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    first = first_part()
    second = second_part()
    x = tolowercase(first + second)
    assert x == ['a','b','c','d','e','f','g','h']

if __name__ == '__main__':
    main()
