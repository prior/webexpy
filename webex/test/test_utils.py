import unittest
from .. import xutils as u
from ..xutils import lazy_property

class UtilsTest(unittest.TestCase):

    def setUp(self): pass
    def tearDown(self): pass

    def test_mpop(self):
        h = {'a':1, 'b':2, 'c':3}
        self.assertIsNone(u.mpop(h,'x','y','z'))
        self.assertEquals({'a':1, 'b':2, 'c':3},h)
        self.assertEquals(1, u.mpop(h,'x','y','z','a'))
        self.assertEquals({'b':2, 'c':3},h)
        self.assertEquals('fallback', u.mpop(h,'x','y','z', fallback='fallback'))
        self.assertEquals(3, u.mpop(h,'x','c','z',fallback='fallback'))

    def test_mget(self):
        h = {'a':1, 'b':2, 'c':3}
        self.assertIsNone(u.mget(h,'x','y','z'))
        self.assertEquals({'a':1, 'b':2, 'c':3},h)
        self.assertEquals(1, u.mget(h,'x','y','z','a'))
        self.assertEquals({'a':1, 'b':2, 'c':3},h)
        self.assertEquals('fallback', u.mget(h,'x','y','z', fallback='fallback'))
        self.assertEquals(3, u.mget(h,'x','c','z',fallback='fallback'))

    def test_lazy_property(self):
        class X(object):
            @lazy_property
            def p(self):
                self.evaluated = True
                return True
        x = X()
        x.evaluated = False
        self.assertTrue(x.p)
        self.assertTrue(x.evaluated)
        x.evaluated = False
        self.assertTrue(x.p)
        self.assertFalse(x.evaluated)
        del x.p
        x.evaluated = False
        self.assertTrue(x.p)
        self.assertTrue(x.evaluated)

    def test_first(self):
        self.assertEquals(None, u.first([0,'',False]))
        self.assertEquals(1, u.first([0,'',1, False]))

    def test_nint(self):
        self.assertEquals(None, u.nint(None))
        self.assertEquals(None, u.nint('23kjsd'))
        self.assertEquals(23, u.nint('23'))

    def test_nstrip(self):
        self.assertEquals(None, u.nstrip(None))
        self.assertEquals(None, u.nstrip(84092))
        self.assertEquals('23', u.nstrip('   23   '))

    def test_sort(self):
        self.assertEquals([1,2,3], u.sort([3,1,2]))
        self.assertEquals([3,2,1], u.sort([3,1,2], lambda a,b: cmp(b,a)))

