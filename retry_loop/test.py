#!/usr/bin/env python

import logging
import pprint
import re
import time
import unittest
from functools import wraps
from mock import patch, call
import retry


class Expected(Exception):
    pass


class BadArguments(TypeError):
    pass


class MismatchedStrings(AssertionError):
    pass


def assertSameListOfStrings(x, y):
    try:
        assert isinstance(x, (list, tuple, set)), x
        assert isinstance(y, (list, tuple, set)), y
        assert len(x) == len(y), (len(x), len(y))
    except AssertionError as ae:
        raise BadArguments(ae.message)
    try:
        for u, v in zip(x, y):
            try:
                assert isinstance(u, (str, unicode)), u
                assert isinstance(v, (str, unicode)), v
            except AssertionError as ae:
                raise BadArguments(ae.message)
            uu = re.sub("\.\.\.", r"(.*)", u.replace("(", r"\(").replace(")", r"\)"))
            assert re.match("^" + uu + "$", v), (u, v)
    except AssertionError as ae:
        raise MismatchedStrings(ae.message)


class TimeAssertListStringsTestCase(unittest.TestCase):
    def test_simple(self):
        assertSameListOfStrings([], [])
        assertSameListOfStrings(['abc'], ['abc'])
        assertSameListOfStrings(['abc', 200 * 'def'], ['abc', 200 * 'def'])

    def test_problems(self):
        with self.assertRaises(MismatchedStrings):
            assertSameListOfStrings(['abc'], ['AbC'])
        with self.assertRaises(MismatchedStrings):
            assertSameListOfStrings(['abc'], ['def'])
        with self.assertRaises(BadArguments):
            assertSameListOfStrings(['abc'], ['abc', 'def'])
        with self.assertRaises(MismatchedStrings):
            assertSameListOfStrings(['abc', 'abc'], ['abc', 'def'])
        with self.assertRaises(BadArguments):
            assertSameListOfStrings(['abc', 'def'], ['abc', 3.14159])

    def test_ellipses(self):
        assertSameListOfStrings(['abc...def'], ['abc AND A BUNCH OF STUFF HERE def'])
        assertSameListOfStrings(['abc...def...'], ['abc AND A BUNCH OF STUFF HERE def'])
        assertSameListOfStrings(['abc...def...'], ['abc AND A BUNCH OF STUFF HERE def YET MORE STUFF'])
        assertSameListOfStrings(['abc...def...ghi'], ['abc STUFF 3.14159265358 def AND MORE STUFF ghi'])
        assertSameListOfStrings(['abc...def...ghi'], ['abc (stuff (that looks) (like lisp)) defghi'])
        with self.assertRaises(MismatchedStrings):
            assertSameListOfStrings(['abc...def...ghi'], ['abc STUFF def'])


def timing(func):
    @wraps(func)
    def inner(*args, **kw):
        before = time.time()
        retval = func(*args, **kw)
        after = time.time()
        logging.debug("{0}:{1}:{2} took {3} seconds".format(
            func.func_code.co_filename,
            func.func_name,
            func.func_code.co_firstlineno,
            after - before
        ))
        return retval
    return inner


class TimeLimitTestCase(unittest.TestCase):
    # Still need tests for process-based time limits

    @retry.enforce_time_limit(seconds=1)
    def slow_function(self, x):
        for _ in range(60):
            time.sleep(.5)
        return x + 1

    @retry.enforce_time_limit(seconds=10)
    def fast_function(self, x):
        for _ in range(2):
            time.sleep(0.1)
        return x + 1

    # @timing
    def test_slow_func(self):
        with self.assertRaises(retry.TimeoutError):
            self.slow_function(2)

    # @timing
    def test_fast_func(self):
        self.assertEquals(self.fast_function(3), 4)


def call_args(call):
    return list(call)[1]


class TestRetryDecorator(unittest.TestCase):
    @patch('logging.error')
    @patch('time.sleep')
    def test_mocks_okay(self, mocksleep, mockerror):
        # make sure mocks will work in retry.py as well as here
        assert retry.time.sleep is mocksleep
        assert retry.logging.error is mockerror

    @patch('logging.error')
    @patch('time.sleep')
    def test_expected_failure(self, mocksleep, mockerror):
        mocksleep.return_value = None
        @retry.retry_on_exception(expected_exception=Expected)
        def foo():
            raise Expected
        foo()
        assertSameListOfStrings([
            'foo(...) failed',
            'foo(...) failed',
            'foo(...) failed',
            'foo(...) failed',
            'foo(...) failed',
            'foo(...) failed'
        ], [call_args(c)[0] for c in mockerror.mock_calls])

    @patch('logging.error')
    @patch('time.sleep')
    def test_last_minute_success(self, mocksleep, mockerror):
        mocksleep.return_value = None
        j = [0]
        @retry.retry_on_exception(expected_exception=Expected)
        def foo():
            j[0] += 1
            if j[0] <= 5:
                raise Expected
        foo()
        assertSameListOfStrings([
            'foo(...) failed',
            'foo(...) failed',
            'foo(...) failed',
            'foo(...) failed',
            'foo(...) failed'
        ], [call_args(c)[0] for c in mockerror.mock_calls])

    @patch('logging.error')
    @patch('time.sleep')
    def test_unexpected_failure(self, mocksleep, mockerror):
        mocksleep.return_value = None
        j = [0]
        @retry.retry_on_exception(expected_exception=Expected)
        def foo():
            raise Exception
        with self.assertRaises(Exception):
            foo()

    @patch('logging.error')
    @patch('time.sleep')
    def test_with_hypothesis(self, mocksleep, mockerror):
        mocksleep.return_value = None
        j = [0]
        @retry.retry_on_exception(hypothesis="working theory", expected_exception=Expected)
        def foo():
            j[0] += 1
            if j[0] <= 5:
                raise Expected
        foo()
        assertSameListOfStrings([
            'foo(...) failed (problem is possibly working theory)',
            'foo(...) failed (problem is possibly working theory)',
            'foo(...) failed (problem is possibly working theory)',
            'foo(...) failed (problem is possibly working theory)',
            'foo(...) failed (problem is possibly working theory)'
        ], [call_args(c)[0] for c in mockerror.mock_calls])


if __name__ == '__main__':
    unittest.main()
