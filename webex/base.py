

class Base(object):
    #URL_PREFIX = 'https://api.citrixonline.com/G2W/rest/'
    #TOKEN = helper.get_creds()['token']
    #ORGANIZER_KEY = helper.get_creds()['organizer_key']
    #TIMEOUT = 20

    def __init__(self):
        super(Base, self).__init__()
#        self.log = logging_glue.get_log('webex.event_controller')

    @property
    def _account(self): raise NotImplementedError() # need to be overridden to point at a valid associated account (to use for auth on querying)


    #@classmethod
    #def _raise(kls, error_kls, result=None):
        #err = result and error_kls(result.status_code, result.text) or error_kls()
        #raise err, None, sys.exc_info()[2]

    #def request(self, body_xml):
        #xml = self.account.request_xml % {'body':body_xml}
        #response = requests.post(url, data=xml)

    ## start and stop expect sanetime times
    #@classmethod
    #def _call(kls, request_xml, subpath, start=None, stop=None):
        #return self.request(VERSION_XML, ('ep:apiVersion','ep:release'))

        #url = '%s/organizers/%s/%s' % (kls.URL_PREFIX, kls.ORGANIZER_KEY, subpath)
        #if start or stop:
            #h = {}
            #if start: h['fromTime']=start.strftime('%Y-%m-%dT%H:%M:%S')
            #if stop: h['toTime']=stop.strftime('%Y-%m-%dT%H:%M:%S')
            #url = "%s?%s" % (url, urlencode(h))
        #headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'OAuth oauth_token=%s'%kls.TOKEN}
        #try:
            #result = requests.get(url, headers=headers, timeout=kls.TIMEOUT)
        #except requests.RequestException:
            #kls._raise(error.Timeout)

        #if result.status_code == 400:
            #kls._raise(error.BadRequest, result)
        #elif result.status_code == 401:
            #if result.text.find('locked'):
                #kls._raise(error.LockedAccount, result)
            #else:
                #kls._raise(error.BadRequest, result)
        #elif result.status_code == 403:
            #kls._raise(error.BadRequest, result)
        #elif result.status_code == 500 or result.status_code==503:
            #kls._raise(error.ServiceDown, result)
        #elif result.status_code != 200:
            #kls._raise(error.Unknown, result)

        #return json.loads(result.text)


#class Organizer(Base):
    #def __init__(self, **key):
        #pass

#class Event(Base):
    #def __init__(self, **kwargs):
        #super(Event, self).__init__()
        #self.start = sanetime(kwargs.get('start') or kwargs.get('startTime'))
        #self.stop = sanetime(kwargs.get('stop') or kwargs.get('stopTime'))
        #self.webinar = webinar

#class Webinar(Base):
    #def __init__(self, **kwargs):
        #super(Webinar, self).__init__()
        #self.key = kwargs.get('webinarKey') or kwargs.get('key')
        #self.subject = kwargs.get('subject')
        #self.description = kwargs.get('description')
        #self.sessions = [Session(webinar=self, start=span['startTime'], stop=span['endTime']) for span in kwargs.get('times',[])]

    #@classmethod
    #def historical(kls, start=None, stop=None):
        #data = kls._call('historicalWebinars', start=start, stop=stop)
        #return [kls(**w) for w in data]

    #@classmethod
    #def upcoming(kls, start=None, stop=None):
        #data = kls._call('upcomingWebinars', start=start, stop=stop)
        #return [kls(**w) for w in data]

    #@classmethod
    #def all(kls, start=None, stop=None):
        #data = kls._call('webinars', start=start, stop=stop)
        #return [kls(**w) for w in data]

    #@classmethod
    #def get(kls, key):
        #return Webinar(**kls._call('webinars/%s'%key))

    
    #@classmethod
    #def get_sessions(kls):
        #return [Session(**s) for s in kls._call('sessions')]

    ##@property
    ##def sessions(self):


    ##@classmethod
    ##def get_meeting_times(kls, key):
        ##webinar = Webinar(key=key)
        ##kls._call('webinars/%s/meetingTimes'%key)
        ##return [Session(webinar=webinar, start=span['startTime']

    #def __repr__(self):
        #return "Webinar(**%s)" % self.__dict__

    #def __str__(self):
        #return self.__dict__


#class Session(Base):
    #def __init__(self, **kwargs):
        #super(Session, self).__init__()
        #self.key = kwargs.get('sessionKey') or kwargs.get('key')
        #self.webinar = kwargs.get('webinar') or kwargs.get('webinarKey') and Webinar(key=kwargs['webinarKey'])
        #self.start = sanetime(kwargs.get('start') or kwargs.get('startTime'))
        #self.stop = sanetime(kwargs.get('stop') or kwargs.get('endTime'))
        #self.attendant_count = kwargs.get('registrantsAttended')

    #def __repr__(self):
        #return "Session(**%s)" % self.__dict__

    #def __str__(self):
        #return self.__dict__

    #def _log(self, action, event=None, level='info'):
        #title = event and event.title or '?'
        #headline = '%s... (event=%s account=%s)' % (action, title, self.account.webex_id)
        #getattr(self.log, level)(headline)
        #if event is not None:
            #self.log.debug('%s...   event=%s   account=%s' % (
                #action,
                #event and pformat(vars(event), width=sys.maxint) or '',
                #pformat(vars(self.account), width=sys.maxint) 
            #))




