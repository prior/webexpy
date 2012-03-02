import unittest2
from .. import error as e
from ..account import Account
from .helper import TestHelper

th = TestHelper()

class AccountTest(unittest2.TestCase):

    def setUp(self): pass
    def tearDown(self): pass

    def test_invalid_account(self):
        with self.assertRaises(e.InvalidAccount): Account()
        with self.assertRaises(e.InvalidAccount): Account(username='test', password='test', site_name='234@234')
        with self.assertRaises(e.InvalidAccount): Account(username='test', password='test')
        with self.assertRaises(e.InvalidAccount): Account(username='test', site_name='test')
        with self.assertRaises(e.InvalidAccount): Account(password='test', site_name='test')

    #def test_version_info(self):
        #self.assertEquals(('WebEx XML API V5.9.0','SP1'), th.account.version_info)
        #self.assertEquals(5.9, th.account.version)
        #self.assertEquals(5, th.account.major_version)

    def test_meetings_require_password(self):
        self.assertTrue(th.account.meetings_require_password)


