from . import utils as u
from sanetime import sanetime

class Registrant(object):
    def __init__(self, event, **kwargs):
        self.event = event
        self.email = u.nstrip(u.mpop(kwargs, 'email'))
        self.id_ = u.nstrip(u.mpop(kwargs, 'attendee_id', 'id', 'id_'))
        self.first_name = u.nstrip(u.mpop(kwargs, 'first_name', 'firstName', 'first'))
        self.last_name = u.nstrip(u.mpop(kwargs, 'last_name', 'lastName', 'last'))
        if kwargs.get('name'): self.name = u.nstrip(kwargs.pop('name'))
        timezone = kwargs.get('timezone', self.event.timezone)
        self.viewings = kwargs.pop('viewings', [])
        started_at = u.mpop(kwargs, 'started_at', 'startTime')
        stopped_at = u.mpop(kwargs, 'stopped_at', 'endTime')
        if started_at and stopped_at:
            self._add_viewing((sanetime(started_at, tz=timezone), sanetime(stopped_at, tz=timezone)))
        self.ip_address = u.nstrip(u.mpop(kwargs, 'ip_address', 'ipAddress'))

    @property
    def name(self):
        return ('%s %s' % (self.first_name or '', self.last_name or '')).strip()

    @name.setter
    def name(self, n):
        parts = n.split(' ')
        self.first_name = ' '.join(parts[0:-1]).strip() or None, 
        self.last_name = parts[-1].strip() or None

    def _add_viewing(self, new_viewing): # assumes viewings are already sorted as they should be
        size = len(self.viewings)
        start_index = 0
        stop_index = size-1
        for i in xrange(size):
            if new_viewing[0] > self.viewings[i][1]:
                start_index = i+1
        for i in xrange(size-1,-1,-1):
            if new_viewing[1] < self.viewings[i][0]:
                stop_index = i-1
        min_ = min(new_viewing[0],start_index<size and self.viewings[start_index][0] or new_viewing[0])
        max_ = max(new_viewing[1],stop_index>=0 and self.viewings[stop_index][1] or new_viewing[1]) 
        self.viewings[start_index:stop_index+1] = [(min_,max_)]

    @property
    def started_at(self):
        self.viewings and self.viewings[0][0] or None

    @property
    def stopped_at(self):
        self.viewings and self.viewings[-1][1] or None

    @property
    def duration(self):
        self.stopped_at and self.started_at and self.stopped_at - self.started_at or None

    def merge(self, registrant):
        for attr in ('email','first_name','last_name','ip_address','id_'):
            if not getattr(self,attr,None): 
                setattr(self,attr,getattr(registrant,attr,None))
        for v in registrant.viewings:
            self._add_viewing(v)

class Account(object):
    pass

class Event(object):
    def __init__(self):
        self._registrants = None
        self._attendees = None
        self._registrants_and_attendees = None

    @property
    def registrants_and_attendees(self):
        if self._registrants_and_attendees == None:
            email_map = dict((r.email,r) for r in self.registrants)
            for a in self.attendees:
                if getattr(a, 'email', None):
                    if a.email in email_map:
                        email_map[a.email].merge(a)
                    else:
                        email_map[a.email] = a
            self._registrants_and_attendees = email_map.values().sort(lambda a,b: cmp(a.email,b.email))
        return self._registrants_and_attendees

    def registrants(self):
        if self._registrants == None:
            email_map = dict((r.email,r) for r in self.registrants)
            for a in self.attendees:
                if getattr(a, 'email', None):
                    if a.email in email_map:
                        email_map[a.email].merge(a)
                    else:
                        email_map[a.email] = a
            self._registrants_and_attendees = email_map.values().sort(lambda a,b: cmp(a.email,b.email))
        return self._registrants_and_attendees
        pass

    def attendees(self):
        self.get_attendees(batch=10)
        pass


    def get_attendees(self, **options):


