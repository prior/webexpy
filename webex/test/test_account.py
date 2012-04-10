import unittest
from .. import error as e
from .. import account
from ..account import Account
from .helper import TestHelper


class AccountTest(unittest.TestCase):

    def setUp(self): 
        self.th = TestHelper()
        self.account = self.th.account

    def tearDown(self): pass

    def test_invalid_account(self):
        with self.assertRaises(e.InvalidAccount): Account()
        with self.assertRaises(e.InvalidAccount): Account(username='test', password='test', site_name='234@234')
        with self.assertRaises(e.InvalidAccount): Account(username='test', password='test')
        with self.assertRaises(e.InvalidAccount): Account(username='test', site_name='test')
        with self.assertRaises(e.InvalidAccount): Account(password='test', site_name='test')
        with self.assertRaises(e.TimeoutError): account.GetVersion(self.account, request_opts={'timeout':0.001}).answer

    def test_constructor(self):
        kwargs = dict(username='amoorthy', password='Thursday123', site_name='hubspoteng')
        account = Account(**kwargs)
        self.assertTrue(account)

    def test_version_info(self):
        self.assertEquals(('WebEx XML API V7.0.0',None), self.account.version_info)
        self.assertEquals(7.0, self.account.version)
        self.assertEquals(7, self.account.major_version)

    def test_meetings_require_password(self):
        self.assertTrue(self.account.meetings_require_password)

    def test_meetings_must_be_unlisted(self):
        self.assertFalse(self.account.meetings_must_be_unlisted)

    @unittest.skip('this can lock the account -- only running when we need to')
    def test_invalid_username_password(self):
        a = self.account
        with self.assertRaises(e.InvalidPasswordError): account.GetSite(Account(username=a.username, password='asdf', site_name=a.site_name)).answer
        with self.assertRaises(e.InvalidUsernameError): account.GetSite(Account(username='asdf', password=a.password, site_name=a.site_name)).answer

