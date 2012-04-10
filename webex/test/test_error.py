import unittest
from ..error import Error
from ..xutils import reraise

class ErrorTest(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self): pass

    def test_wrapped_error(self):
        with self.assertRaisesRegexp(Error, 'custom inner description'):
            try:
                self.outer_function(inner_error=True)
            except Exception as err:
                reraise(Error("extra info", err=err))

        with self.assertRaisesRegexp(Error, 'extra info'):
            try:
                self.outer_function(inner_error=True)
            except Exception as err:
                reraise(Error("extra info", err=err))

    def outer_function(self, outer_error=False, inner_error=False):
        if outer_error:
            raise ValueError('custom outer description')
        return self.inner_function(inner_error)

    def inner_function(self, error=False):
        if error:
            raise ValueError('custom inner description')
        return None
