import os
import json

from webex.webex import WebEx, WebExError
 

def webex_from_test_credentials(debug = True):
    filename = 'test_credentials.json'

    try:
        raw_text = open(os.path.join(os.path.dirname(__file__), filename)).read()
    except IOError, err:
        raise WebExError, """Unable to open '%s' for integration tests.\n
  These tests rely on the existence of that file and on it having valid webex credentials.""" % filename

    try:
        creds = json.loads(raw_text)
    except ValueError, err:
        raise WebExError, """'%s' doesn't appar to be valid json!\n
  These tests rely on the existence of that file and on it having valid webex credentials.""" % filename

    return WebEx(debug=debug, **creds) 
