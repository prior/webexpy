import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

def get_log(cls=None, subname=None):
    cls_part = cls and '.%s'%str(cls).split("'")[1].split('.')[-1] or ''
    subname_part = subname and '.%s'%subname.strip() or ''
    name = 'webex%s%s' % (subname_part, cls_part)
    logger = logging.getLogger(name)
    logger.addHandler(NullHandler())
    return logger

