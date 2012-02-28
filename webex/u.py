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

