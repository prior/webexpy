from request import Request
from response import Response
from utils import EP_NS, SITE_NS

GET_XML = """
<bodyContent xsi:type="java:com.webex.service.binding.site.GetSite" />
"""

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
        self._major_version = None

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
        release_elem = xml_out.find("{%s}release"%EP_NS)
        release = release_elem is not None and release_elem.text or ""
        return "%s : %s" % (version, release)

    @property
    def major_version(self):
        if not self._major_version:
            version = self.get_api_version()
            number = float('.'.join(version.split(' : ')[0].split(' ')[-1].split('V')[-1].split('.')[:2]))
            self._major_version = int(number)
        return self._major_version

    def query(self, body_content, empty_list_ok=False):
        return Response(Request(self.account, body_content), xml_override=getattr(self,'xml_override',None), empty_list_ok=empty_list_ok)

    #TODO: should attempt to deal with things moving underneath it since there's no way to page through this thing with any certainty
    def assemble_batches(self, listing_function, **options):
        batch_size = min(options.pop('batch_size', 10), 500) # can't go over 50 with some methods
        start_from = options.pop('start_from',None) or options.pop('startFrom',1)
        offset = options.pop('offset', start_from-1)
        max_ = options.pop('max',None) or options.get('max_number',None) or options.get('maxNumber',None)
        pre_callback = options.pop('pre_callback',None)
        item_id = options.pop('item_id',None)

        items = {}
        batch_number = 1
        original_offset = offset
        batch_count = 0
        item_count = 0
        while True:
            local_max = max(min(max_ is None and batch_size or (max_-item_count), batch_size),0)
            options['list_options_xml'] = LIST_OPTIONS_XML % (offset+1, local_max)
            options['batch_number'] = batch_number
            pre_callback and pre_callback(batch_number)
            new_items,batch_count,total_count = listing_function(**options)
            item_count += batch_count
            for o in new_items:
                id_ = item_id and getattr(o,item_id) or id(o)
                if items.get(id_):
                    items[id_] = items[id_].merge(o)
                else:
                    items[id_] = o
            if batch_count < batch_size or max_ and item_count>=max_:
                break
            offset += batch_size
            batch_number += 1
        return (items.values(), offset+batch_count-original_offset)

    def determine_count(self, listing_function):
        options = {}
        options['list_options_xml'] = LIST_OPTIONS_XML % (1,1)
        options['batch_number'] = 0
        return listing_function(**options)[2]


    @property
    def password_required(self):
        response = self.query(GET_XML)
        if response.success:
            parent_elem = response.body_content.find("{%s}siteInstance"%SITE_NS)
            if parent_elem is None: return None
            security_elem = parent_elem.find("{%s}securityOptions"%SITE_NS)
            if security_elem is None: return None
            password_elem = security_elem is not None and security_elem.find("{%s}allMeetingsPassword"%SITE_NS)
            if password_elem is None: return None
            return password_elem.text.lower()=='true'
        return None
