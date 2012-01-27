class Attendee(object):
    def __init__(self, email=None, first_name=None, last_name=None, started_at=None, stopped_at=None, duration=None, ip_address=None, attendee_id=None):
        super(Attendee,self).__init__()
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.started_at = started_at
        self.stopped_at = stopped_at
        self.duration = duration
        self.ip_address = ip_address
        self.attendee_id = attendee_id

    def merge(self, attendee):
        self.email = self.email or attendee.email
        self.first_name = self.first_name or attendee.first_name
        self.last_name = self.last_name or attendee.last_name
        self.ip_address = self.ip_address or attendee.ip_address

        if self.started_at and attendee.started_at:
            if attendee.started_at < self.started_at:
                self.started_at = attendee.started_at
        self.started_at = self.started_at or attendee.started_at

        if self.stopped_at and attendee.stopped_at:
            if attendee.stopped_at > self.stopped_at:
                self.stopped_at = attendee.stopped_at
        self.stopped_at = self.stopped_at or attendee.stopped_at

        if self.duration and attendee.duration:
            self.duration += attendee.duration
        self.duration = self.duration or attendee.duration

        return self

    def __str__(self):
        return self.__unicode__() 

    def __unicode__(self):
        return "%s (%s %s) {%s-%s for %sm} [%s] %s" % (self.email, self.first_name, self.last_name, self.started_at, self.stopped_at, self.duration, self.ip_address, self.id)


