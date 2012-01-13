from request import Request
from response import Response
from utils import EP_NS

LIST_OPTIONS_XML = """
  <listControl>
    <startFrom>%s</startFrom>
    <maximumNum>%s</maximumNum>
  </listControl>
"""

class BaseController(object):

    def __init__(self, account):
        super(BaseController,self).__init__()
        self.account = account

    def _log(self):
        pass

    def debug(self, *args, **options):
        options['level'] = 'debug'
        return self._log(*args, **options)

    def info(self, *args, **options):
        options['level'] = 'info'
        return self._log(*args, **options)

    def warn(self, *args, **options):
        options['level'] = 'warn'
        return self._log(*args, **options)

    def error(self, *args, **options):
        options['level'] = 'error'
        return self._log(*args, **options)

    def get_api_version(self):
        xml_in = "\n<bodyContent xsi:type=\"java:com.webex.service.binding.ep.GetAPIVersion\"></bodyContent>"
        xml_out = self.query(xml_in).body_content
        version = xml_out.find("{%s}apiVersion"%EP_NS).text
        release = xml_out.find("{%s}release"%EP_NS).text
        return "%s : %s" % (version, release)

    def query(self, body_content, empty_list_ok=False):
        return Response(Request(self.account, body_content), xml_override=getattr(self,'xml_override',None), empty_list_ok=empty_list_ok)

    # attempts to deal with things moving underneath it by always going back halfway in batches-- effectively querying the entire thing twice over (cuz there's no other way to page through this thing with any certainty)
    def assemble_batches(self, listing_function, **options):
        batch_size = min(options.pop('batch_size', 10), 500) # can't go over 50 with some methods
        start_from = options.pop('start_from',None) or options.pop('startFrom',1)
        offset = options.pop('offset', start_from-1)
        max_ = options.pop('max',None) or options.get('max_number',None) or options.get('maxNumber',None)
        pre_callback = options.pop('pre_callback',None)
        item_id = options.pop('item_id',None)

        items = {}
        batch_number = 1
        while True:
            local_max = min(max_ and (max_-offset) or batch_size, batch_size)
            options['list_options_xml'] = LIST_OPTIONS_XML % (offset+1, local_max)
            options['batch_number'] = batch_number
            pre_callback and pre_callback(batch_number)
            new_items = listing_function(**options)
            for o in new_items:
                items[item_id and getattr(o,item_id) or id(o)] = o
            if len(new_items) < batch_size or len(items)==max_:
                break;
            offset += batch_size
            batch_number += 1
        return items.values()

