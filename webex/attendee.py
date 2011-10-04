from utils import is_blank

class Attendee(object):
    def __init__(self, email=None, first_name=None, last_name=None, start_datetime=None, end_datetime=None, duration=None, ip_address=None, id=None):
        super(Attendee,self).__init__()
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.duration = duration
        self.ip_address = ip_address
        self.id = id

    def merge(self, attendee):
        if is_blank(self.email) and not is_blank(attendee.email):
            self.email = attendee.email
        if is_blank(self.first_name) and not is_blank(attendee.first_name):
            self.first_name = attendee.first_name
        if is_blank(self.last_name) and not is_blank(attendee.last_name):
            self.last_name = attendee.last_name
        if self.start_datetime is None and attendee.start_datetime is not None:
            self.start_datetime = attendee.start_datetime
        elif self.start_datetime is not None and attendee.start_datetime is not None and attendee.start_datetime < self.start_datetime:
            self.start_datetime = attendee.start_datetime
        if self.end_datetime is None and attendee.end_datetime is not None:
            self.end_datetime = attendee.end_datetime
        elif self.end_datetime is not None and attendee.end_datetime is not None and attendee.end_datetime > self.end_datetime:
            self.end_datetime = attendee.end_datetime
        if self.duration is None and attendee.duration is not None:
            self.duration = attendee.duration
        elif self.duration is not None and attendee.duration is not None:
            self.duration += attendee.duration
        if is_blank(self.ip_address) and not is_blank(attendee.ip_address):
            self.ip_address = attendee.ip_address
        return self

    def __str__(self):
        return self.__unicode__() 

    def __unicode__(self):
        return "%s (%s %s) {%s-%s for %sm} [%s] %s" % (self.email, self.first_name, self.last_name, self.start_datetime, self.end_datetime, self.duration, self.ip_address, self.id)
        #return "WebEx Attendee: %s started watching at %s and ended at %s. (invited: %s, registered %s)" % (self.email, self.start_datetime, self.end_datetime, self.invited, self.registered)


