import unittest2
from webex.error import WebExError
from webex.base_controller import BaseController
from webex.event_controller import EventController
import helper

# these integration tests are normally commented out so we don't incur their hits on every run of our test suite
class BaseControllerTest(unittest2.TestCase):

    def setUp(self):
        self.account = helper.get_account()

    def test_bad_account(self):
        self.account.webex_id = 'bad_webex_id'
        self.account.password = 'bad_password'
        self.account.rebuild_request_xml_template()
        with self.assertRaises(WebExError):
            EventController(self.account, debug=True).list()

    def test_invalid_site_name(self):
        self.account.site_name = 'invalid_si@#$%^te_name'
        self.account.rebuild_request_xml_template()
        with self.assertRaises(WebExError):
            EventController(self.account, debug=False).list()

    def test_wrong_site_name(self):
        self.account.site_name = 'bad_site_name'
        self.account.rebuild_request_xml_template()
        with self.assertRaises(WebExError):
            EventController(self.account, debug=False).list()

    def test_version(self):
        self.assertIn('API V5.9.', BaseController(self.account, debug=False).get_api_version())


if __name__ == '__main__':
    unittest2.main()
