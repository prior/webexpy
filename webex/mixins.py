from sanetime import delta

class Event(object):
    @property
    def starts_at(self): return self._starts_at or self._started_at
    @starts_at.setter
    def starts_at(self, starts_at): self._starts_at = starts_at
    
    @property
    def ends_at(self): return self._ends_at or self._ended_at
    @ends_at.setter
    def ends_at(self, ends_at): self._ends_at = ends_at

    @property
    def started_at(self): return self._started_at or self._starts_at
    @started_at.setter
    def started_at(self, started_at): self._started_at = started_at

    @property
    def ended_at(self): return self._ended_at or self._ends_at
    @ended_at.setter
    def ended_at(self, ended_at): self._ended_at = ended_at

    @property
    def duration_in_minutes(self): return self.scheduled_duration_in_minutes or self.actual_duration_in_minutes
    @duration_in_minutes.setter
    def duration_in_minutes(self, minutes):
        self.scheduled_duration_in_minutes = minutes
    
    @property
    def scheduled_duration_in_minutes(self): return self._starts_at and self._ends_at and (self._ends_at-self._starts_at).m
    @scheduled_duration_in_minutes.setter
    def scheduled_duration_in_minutes(self, minutes):
        if self._starts_at: self._ends_at = self._starts_at + delta(m=minutes)
        elif self._ends_at: self._starts_at = self._ends_at - delta(m=minutes)

    @property
    def actual_duration_in_minutes(self): return self._started_at and self._ended_at and (self._ended_at-self._started_at).m
    @actual_duration_in_minutes.setter
    def actual_duration_in_minutes(self, minutes):
        if self._started_at: self._ended_at = self._started_at + delta(m=minutes)
        elif self._ended_at: self._started_at = self._ended_at - delta(m=minutes)
    
    @property
    def scheduled_duration(self): return self.scheduled_duration_in_minutes
    @scheduled_duration.setter
    def scheduled_duration(self, minutes): self.scheduled_duration_in_minutes = minutes

    @property
    def actual_duration(self): return self.actual_duration_in_minutes
    @actual_duration.setter
    def actual_duration(self, minutes): self.actual_duration_in_minutes = minutes

    @property
    def duration(self): return self.duration_in_minutes
    @duration.setter
    def duration(self, minutes): self.duration_in_minutes = minutes

    @property
    def scheduled_timezone(self):
        return self._starts_at and self._starts_at.tz or self._ends_at and self._ends_at.tz
    @property
    def actual_timezone(self):
        return self._started_at and self._started_at.tz or self._ended_at and self._ended_at.tz
    @property
    def timezone(self):
        return self.scheduled_timezone or self.actual_timezone

    @property
    def duration_short_string(self):
        if self.duration_in_minutes <= 90: return "%sm" % self.duration_in_minutes
        return "%.1fh" % (self.duration_in_minutes / 60.0)

