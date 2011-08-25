import unittest2
import os

from webex.webex import WebEx
from webex.event import WebExEvent
from webex.timezone import WebExTimezone
from webex.event_controller import WebExEventController
from webex.response import WebExResponse

class TestWebExForcedXml(WebEx):
    def __init__(self, forced_xml):
        self.forced_xml = forced_xml
    def query(self, body_content):
        return WebExResponse(None, xml_override=self.forced_xml)


class WebExTest(unittest2.TestCase):
    def test_list_events_response_parsing(self):
        webex = TestWebExForcedXml(open(os.path.join(os.path.dirname(__file__),'example_LstsummaryEventResponse.xml')).read())
        event_list = WebExEventController(webex).list_events()
        self.assertEqual(3, len(event_list))
        event = event_list[0]
        self.assertIsNotNone(event)
        self.assertEquals("ec 0000000000", event.session_name)
        self.assertEquals(WebExTimezone(45).localize_new_naive_datetime(2004,4,3,10), event.start_datetime)
        self.assertEquals(60, event.duration)
        self.assertEquals('xbxbxcxcbbsbsd', event.description)
        self.assertEquals('23357393', event.session_key)

    def test_create_event_response_parsing(self):
        webex = TestWebExForcedXml(open(os.path.join(os.path.dirname(__file__),'example_CreateEventResponse.xml')).read())
        event = WebExEvent("ec 000000000", WebExTimezone(45).localize_new_naive_datetime(2004,4,3,10), 60, 'xbxbxbxbxxxbx')
        self.assertIsNone(event.session_key)
        WebExEventController(webex).create_event(event)
        self.assertIsNotNone(event.session_key)

if __name__ == '__main__':
    unittest2.main()
