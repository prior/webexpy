class Event(object):
    def __init__(self, title=None, starts_at=None, duration=60, description=None, session_key=None):
        super(Event,self).__init__()
        self.title = title
        self.starts_at = starts_at
        self.duration = duration
        self.description = description
        self.session_key = session_key

    def __str__(self):
        return self.__unicode__() 

    def __unicode__(self):
        return "WebEx Event: %s %s at %s for %s minutes [%s]" % (self.title, self.description, self.starts_at, self.duration, self.session_key)

