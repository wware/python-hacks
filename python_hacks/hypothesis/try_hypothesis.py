import logging
import unittest
from hypothesis import given
from hypothesis.strategies import integers

"""
This example is taken from
https://vknight.org/unpeudemath/code/2016/03/07/Property-based-testing-and-finding-a-bug.html

Some other Hypothesis resources:
http://elliot.land/post/unit-tests-that-write-themselves-property-based-testing-using-hypothesis-in-python
https://medium.com/homeaway-tech-blog/write-better-python-with-hypothesis-5b31ac268b69
https://stackoverflow.com/questions/39561310/generating-list-of-lists-with-custom-value-limitations-with-hypothesis
https://stackoverflow.com/questions/39670903/random-sampling-with-hypothesis
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def divisible_by_11(number):
    """
    A number is divisible by 11 if and only if the alternating (in sign)
    sum of the number's digits is divisible by 11.

    :param number: the number to be tested
    :type number: int
    :return: true if and only if the number is divisible by 11
    """
    assert number > 0
    logging.debug(number)
    string_number = str(number)
    alternating_sum = sum([
        ((-1) ** i) * int(d)
        for i, d in enumerate(string_number)
    ])
    if alternating_sum < 0:
        # make it positive while preserving its modulo-11 value
        alternating_sum += 11 * (1 + ((-alternating_sum) / 11))
    # number is divisible by 11 if alternating_sum is divisible by 11
    if alternating_sum < 12:
        return alternating_sum in [0, 11]
    else:
        return divisible_by_11(alternating_sum)


class TestDivisible(unittest.TestCase):
    @given(k=integers(min_value=1))
    def test_divisible_by_11(self, k):
        self.assertTrue(divisible_by_11(11 * k))
        self.assertFalse(divisible_by_11(11 * k + 1))
        self.assertFalse(divisible_by_11(11 * k + 10))


if __name__ == '__main__':
    unittest.main()
