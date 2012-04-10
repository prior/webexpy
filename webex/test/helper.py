import os
import json
from ..xutils import lazy_property, reraise
from ..account import Account

TEST_ACCOUNTS_FILENAME = 'test_accounts.json'
COMMON_DISCLAIMER = """
Unittests rely on the existence of the file: '%s', and on it having valid credentials at least for the 'default' key.  See %s.example for what this file should look like.  
Unittests are designed to be non-destructive to current data on the account.  
Of course a bug could break that design, but precluding that, you should be able to run these unittests on your webex account without it affecting the current state of things.
""" % (TEST_ACCOUNTS_FILENAME, TEST_ACCOUNTS_FILENAME)

class TestError(ValueError): pass

class TestHelper(object):
    def __init__(self, **kwargs):
        super(TestHelper, self).__init__()

    def __getitem__(self, key):
        try:
            return Account(**self._accounts_dict[key])
        except KeyError:
            reraise(TestError("%s doesn't appear to have a 'default' key.  Unittest rely on the creds specified under that key.\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)))

    @lazy_property
    def account(self):
        return self.__getitem__('default')

    @lazy_property
    def _accounts_dict(self):
        try:
            raw_text = open(os.path.join(os.path.dirname(__file__), TEST_ACCOUNTS_FILENAME)).read()
        except IOError:
            reraise(TestError("Unable to open '%s' for integration tests.\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)))
        try:
            d = json.loads(raw_text)
        except ValueError:
            reraise(TestError("'%s' doesn't appear to be valid json!\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)))
        return d



#def generate_attendee(event=None):
    #random = str(uuid4())
    #return Attendee(email='%s@%s.com'%(random[0:8],random[8:16]), first_name='John%s'%random[16:20], last_name='Smith%s'%random[20:24])
