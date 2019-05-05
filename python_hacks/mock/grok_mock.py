#!/usr/bin/env python
"""
Mock can be extremely confusing. Here's an attempt to clarify it.
http://www.voidspace.org.uk/python/mock/patch.html
http://mock.readthedocs.org/en/latest/index.html
"""

import argparse
import logging
import os
import pydoc
import sys
import unittest
try:
    from unittest.mock import MagicMock, patch, call
except ImportError:
    from mock import MagicMock, patch, call


#############################################
#############################################


class Foo(object):
    """
    A little class that we want to test
    """
    def add_five(self, x):
        """
        An extremely complex and nuanced class method.
        """
        return x + 5

RealFoo = Foo     # testing convention: RealFoo will never be a mock

def add_ten(ignored, x):
    """
    This will be used to temporarily replace the Foo.add_five method.
    """
    return x + 10


#############################################
#############################################


class MyTestCase(unittest.TestCase):

    """
    A bunch of tests for the little class
    """

    def test_0_normal_foo_behavior(self):
        """
        Vanilla test of the normal add-five behavior of Foo.add_five(). Tests are
        done in ASCII order by name, so the "0" in the name makes this test run
        before the others.
        """
        foo = Foo()
        self.assertEqual(11, foo.add_five(6))

    @patch('__main__.Foo')
    def test_monkeypatch_argument(self, mock_foo):
        """
        In this usage, @patch() substitutes a MagicMock for a function's argument.
        What we are doing here, for as long as we are inside the function, is we
        are monkey-patching __main__ so that its 'Foo' attribute is no longer the
        class defined above, it is the mock.

        So "@patch('__main__.Foo')" is saying, get the module whose name is
        '__main__', create a mock, temporarily setattr the module's "Foo" to
        refer to the mock instead of the class, and undo that when the function
        finishes.
        """
        assert mock_foo is Foo
        assert isinstance(Foo, MagicMock)
        assert not isinstance(Foo, RealFoo)

    @patch('__main__.Foo')
    @patch('__main__.Foo.add_five')
    def test_monkeypatch_multiple_arguments(self, mock_add_five, mock_foo):
        """
        @patch() is applied to arguments in reverse order
        """
        assert isinstance(mock_add_five, MagicMock)
        assert isinstance(mock_foo, MagicMock)
        assert mock_foo is Foo
        mock_add_five(None, 4)
        assert mock_add_five.mock_calls == [call(None, 4)]

    def test_patch_in_with_statement(self):
        """
        You don't need to use patch() as a function decorator. You can use it in a
        "with" statement and then it applies for the duration of the code block. If
        you write "as", then you're creating a second name for the mock, which can
        be useful to remind yourself that it's really a mock.

        MockFoo.return_value is the thing returned by the Foo() constructor, and
        it is another MagicMock. When we assign the return value of its add_five
        "method", we can then perform a method call with predictable results.
        """
        assert Foo is RealFoo
        with patch('__main__.Foo') as MockFoo:
            assert Foo is MockFoo
            assert Foo is not RealFoo
            instance = MockFoo.return_value
            assert isinstance(instance, MagicMock)
            assert isinstance(instance.add_five, MagicMock)
            instance.add_five.return_value = 'baz'
            assert Foo() is instance
            assert Foo().add_five() == 'baz'
        assert Foo is RealFoo

    def test_patcher_start_and_stop(self):
        """
        We can use the start and stop methods of the patcher returned by patch() to
        explicitly control when the patching turns on and off. Also, we can use
        "spec=True" to create a mock class that has mock methods corresponding to the
        real methods in Foo. We will have all the same methods that Foo has, but the
        methods themselves will all be MagicMock objects.
        """
        patcher = patch('__main__.Foo', spec=True)
        assert not isinstance(Foo, MagicMock)
        assert Foo is RealFoo
        try:
            patcher.start()
            assert isinstance(Foo, MagicMock)
            assert Foo is not RealFoo
            import inspect
            assert False, inspect.getmro(Foo)
            assert issubclass(Foo.__class__, RealFoo.__class__)
            instance = Foo()
            assert isinstance(instance, RealFoo)
            assert hasattr(instance, 'add_five')
            assert isinstance(instance.add_five, MagicMock)
            # instance.add_five method is a mock, but let's try calling it anyway
            six_plus_five = instance.add_five(6)
            assert isinstance(six_plus_five, MagicMock)
            with self.assertRaises(Exception):
                # instance.add_five is a mock, so it doesn't know it should add 5
                assert six_plus_five == 11
        finally:
            # FUN FACT - if we hit an exception before reaching this "patcher.stop()"
            # statement, then Foo will never be unmocked, so test_z_normal_foo_behavior()
            # will fail
            patcher.stop()
        assert Foo is RealFoo
        assert instance.method_calls == [call.add_five(6)]

    @patch('__main__.Foo.add_five', new=add_ten)
    def test_patch_replace_method(self):
        """
        We can patch a replacement method into a class, and the replacement lasts
        for only the duration of this test method. In this case there are no
        MagicMock instances anywhere.
        """
        foo = Foo()
        self.assertEqual(16, foo.add_five(6))

    def test_z_normal_foo_behavior(self):
        """
        Repeat the normal test after all the others, to make sure that all
        the patches have been reverted as expected.
        """
        self.test_0_normal_foo_behavior()


#############################################
##                 main()                  ##
#############################################


def main():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description=__doc__
    )
    parser.add_argument(
        '-D', '--docstrings',
        action='store_true',
        help='show all the docstrings using pydoc'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='turn on verbosity and debug-level debugging output',
    )
    options = parser.parse_args()
    logging.basicConfig(
        format='%(asctime)-15s  %(levelname)s  %(filename)s:%(lineno)d  %(message)s',
        level=(logging.DEBUG if options.verbose else logging.INFO)
    )
    if options.docstrings:
        doc = pydoc.TextDoc()
        pager = pydoc.getpager()
        pager(doc.docmodule(sys.modules[__name__]))
    else:
        suite = unittest.TestLoader().loadTestsFromTestCase(MyTestCase)
        unittest.TextTestRunner(verbosity=(2 if options.verbose else 0)).run(suite)


if __name__ == '__main__':
    main()
