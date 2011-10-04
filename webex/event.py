class Event(object):
    def __init__(self, session_name=None, start_datetime=None, duration=60, description=None, session_key=None):
        super(Event,self).__init__()
        self.session_name = session_name
        self.start_datetime = start_datetime
        self.duration = duration
        self.description = description
        self.session_key = session_key

    def __str__(self):
        return self.__unicode__() 

    def __unicode__(self):
        return "WebEx Event: %s %s at %s for %s minutes [%s]" % (self.session_name, self.description, self.start_datetime, self.duration, self.session_key)

