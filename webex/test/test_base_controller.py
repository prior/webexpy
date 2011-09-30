import unittest2
from nose.plugins.attrib import attr
from webex.error import WebExError
from webex.base_controller import BaseController
from webex.event_controller import EventController
import helper

# these integration tests are normally commented out so we don't incur their hits on every run of our test suite
class BaseControllerTest(unittest2.TestCase):

    def setUp(self):
        self.account = helper.get_account()

    @attr('api')
    def test_bad_account(self):
        self.account.webex_id = 'bad_webex_id'
        self.account.password = 'bad_password'
        with self.assertRaises(WebExError):
            self.account.rebuild_request_xml_template()
            EventController(self.account, debug=False).list()

    def test_invalid_site_name(self):
        self.account.site_name = 'invalid_si@#$%^te_name'
        with self.assertRaises(WebExError):
            self.account.rebuild_request_xml_template()
            EventController(self.account, debug=False).list()

    @attr('api')
    def test_wrong_site_name(self):
        self.account.site_name = 'bad_site_name'
        with self.assertRaises(WebExError):
            self.account.rebuild_request_xml_template()
            EventController(self.account, debug=False).list()

    @attr('api')
    def test_version(self):
        self.assertIn('API V5.9.', BaseController(self.account, debug=False).get_api_version())


if __name__ == '__main__':
    unittest2.main()
