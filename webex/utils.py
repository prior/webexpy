import sys
from . import namespace as ns
from . import error

def first(list_):
    for l in list_:
        if l: return l
    return None

def mpop(d, *args, **kwargs):
    return first((d.pop(a,None) for a in args)) or kwargs.get('fallback',None)

def mget(d, *args, **kwargs):
    return first((d.get(a,None) for a in args)) or kwargs.get('fallback',None)

def nint(s):
    try:
        return int(s)
    except:
        return None

def nstrip(s):
    try:
        return s.strip() or None
    except:
        return None

def nlower(s):
    if s is None: return None
    return s.lower()


def sort(item, *args, **kwargs):
    item.sort(*args, **kwargs)
    return item


class lazy_property(object):
    def __init__(self, f):
        super(lazy_property, self).__init__()
        self.f = f
        self.attr = '_lazy_%s' % f.__name__

    def __get__(self, obj, type=None):
        if not hasattr(obj, self.attr):
            setattr(obj, self.attr, self.f(obj))
        return getattr(obj, self.attr)

    def __delete__(self, obj):
        if hasattr(obj, self.attr):
            delattr(obj, self.attr)

def _namespaced_tag(tag):
    parts = tag.split(':')
    if len(parts)>=2:
        parts[0] = "{%s}%s" % (ns.PREFIXES[parts[0]], parts[1])
    return parts[0]

def find(elem, *args):
    try:
        for a in args: elem = elem.find(_namespaced_tag(a))
    except:
        reraise(error.ParseError())
    return elem

def nfind(elem, *args):
    try:
        elem = find(elem, *args)
    except error.ParseError:
        return None
    return elem

def nfind_str(elem, *args):
    elem = nfind(elem, *args)
    if elem is None: return None
    return elem.text

def nfind_lstr(elem, *args):
    s = nfind_str(elem, *args)
    if s is None: return None
    return s.lower()

def nfind_int(elem, *args):
    elem = nfind(elem, *args)
    if elem is None: return None
    return int(elem.text)

def find_all(elem, *args):
    elem = find(elem, *args[0:-1])
    return elem.findall(_namespaced_tag(args[-1]))

def reraise(err):
    raise err, None, sys.exc_info()[2]


def grab(root, *args, **kwargs):
#    import pdb; pdb.set_trace()
    ns = kwargs.pop('ns',None)
    attrs_labels = dict((a,ns and len(a.split(':'))==1 and '%s:%s'%(ns,a) or a) for a in args)
    return dict((k, (nfind_str(root,v))) for k,v in attrs_labels.iteritems())



        
        #u.traverse(elem.
        
        
        #if response.success:
            #for elem in response.body_content.findall('{%s}matchingRecords'%EVENT_NS):
                #total_count = int(elem.find('{%s}total'%SERVICE_NS).text)
            #for elem in response.body_content.findall("{%s}event"%EVENT_NS):
                #title = elem.find("{%s}sessionName"%EVENT_NS).text
                #starts_at = elem.find("{%s}startDate"%EVENT_NS).text
                #timezone_id = int(elem.find("{%s}timeZoneID"%EVENT_NS).text)
                #duration = int(elem.find("{%s}duration"%EVENT_NS).text)
                #description = elem.find("{%s}description"%EVENT_NS).text
                #session_key = elem.find("{%s}sessionKey"%EVENT_NS).text
                #starts_at = sanetztime(starts_at, tz=timezone.WEBEX_TIMEZONE_ID_TO_PYTZ_LABEL_MAP[timezone_id])
                #event = Event(title, starts_at, duration, description, session_key)
                #events.append(event)
                #batch_count +=1

