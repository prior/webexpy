def first(list_):
    for l in list_:
        if l: return l
    return None

def mpop(d, *args):
    return first((d.pop(a,None) for a in args))

def mget(d, *args):
    return first((d.get(a,None) for a in args))

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



