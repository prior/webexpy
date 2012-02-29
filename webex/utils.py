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

def _namespaced_label(label):
    parts = label.split(':')
    if len(parts)>=2:
        parts[0] = "{%s}%s" % (ns.PREFIXES[parts[0]], parts[1])
    return parts[0]

def traverse(el, *args):
    try:
        for a in args: el = el.find(_namespaced_label(a))
    except:
        reraise(error.ParseError())
    return el

def ntraverse(el, *args):
    try:
        for a in args: 
            el = el.find(_namespaced_label(a))
            if el is None: return None
    except:
        reraise(error.ParseError())
    return el

def ntraverse_text(el, *args):
    el = traverse(el, *args)
    if el is None: return None
    return el.text

def reraise(err):
    raise err, None, sys.exc_info()[2]


