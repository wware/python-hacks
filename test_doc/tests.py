#!/usr/bin/env python

import argparse
import os
import unittest
from functional import add, Foo


class TestMyStuff(unittest.TestCase):
    def test_add(self):
        self.assertEquals(add(4, 2), 6)
        self.assertEquals(add(3, 19), 22)

    def test_Foo(self):
        f = Foo()
        self.assertTrue(isinstance(f, Foo))
        self.assertEquals(f.add_five(3), 8)


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        '--pdb',
        action='store_true',
        help='run PDB',
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='more verbose output',
    )
    opts = parser.parse_args()
    if opts.pdb:
        import pdb
        pdb.set_trace()
    suite = unittest.TestSuite()
    for method in dir(TestMyStuff):
        if method.startswith("test"):
            suite.addTest(TestMyStuff(method))
    runner = unittest.TextTestRunner(verbosity=(2 if opts.verbose else 0))
    x = runner.run(suite)
    if False and len(x.errors) + len(x.failures) == 0:
        os.unlink(outf.name)


if __name__ == '__main__':
    main()
