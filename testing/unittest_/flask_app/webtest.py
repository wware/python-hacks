import json
import unittest

from web import foo_endpoint, bar_endpoint, baz_endpoint


class TestStringMethods(unittest.TestCase):

    def test_foo(self):
        self.assertEqual(json.loads(foo_endpoint()), {"data": "foo"})

    def test_foo_wrong(self):
        with self.assertRaises(AssertionError):
            self.assertEqual(json.loads(foo_endpoint()), {"data": "meh"})

    def test_bar(self):
        self.assertEqual(json.loads(bar_endpoint()), {"data": "bar"})

    def test_baz(self):
        self.assertEqual(json.loads(baz_endpoint()), {"data": "baz"})

if __name__ == '__main__':
    unittest.main(verbosity=2)
