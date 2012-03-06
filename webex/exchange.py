import sys
import requests
import requests.async
from .utils import find, nfind_str, nfind_int, reraise, lazy_property, grab
from . import error
from lxml import etree

# This class is the way it is to allow for synchronous and asynchronous calling possibilities (though after building things this way, it appears that webex allows zero-to-none concurrency on a single account domain-- fuck)
class Exchange(object):
    def __init__(self, account, request_opts=None, **opts):
        super(Exchange, self).__init__()
        self.account = account
        self.request_opts = {'timeout':10, 'config':dict(verbose=sys.stderr)}
        self.request_opts.update(request_opts or {})
        self.opts = opts
#        self.opts['debug']=True

    def process_response(self, response=None):
        if self.opts.get('debug'): print etree.tostring(etree.fromstring(str(self.request.data)), pretty_print=True)
        try:
            if response:
                response.raise_for_status()
            else:
                response = self.response
        except requests.exceptions.Timeout:
            reraise(error.TimeoutError(self.request))
        except requests.exceptions.RequestException:
            if response is None or response.status_code==0:
                reraise(error.RequestError(self.request, str(response.error)))
            else:
                reraise(error.ResponseError(response))
        if response.status_code != 200:
            raise error.ResponseError(response)
        try:
            root = etree.fromstring(response.content)
        except:
            reraise(error.ParseError(response.content))
        if self.opts.get('debug'): print etree.tostring(etree.fromstring(response.content), pretty_print=True)
        resp = find(root, 'serv:header', 'serv:response')
        success = find(resp, 'serv:result').text.lower() == "success"
        gsb_status = nfind_str(resp, 'serv:gsbStatus')
        exception_id = nfind_int(resp, 'serv:exceptionID')
        reason = nfind_str(resp, 'serv:reason')
        value = nfind_str(resp, 'serv:value')
        if exception_id: raise error.ApiError(success, exception_id, reason, value, gsb_status)
        self._lazy_answer = self._answer(find(root, 'serv:body', 'serv:bodyContent'))
        return self._lazy_answer

    def _answer(self, body_content):
        raise NotImplementedError("this needs to be implemented in a derived class")

    def _input(self):
        raise NotImplementedError("this needs to be implemented in a derived class")
    
    @lazy_property
    def request(self):
        #return self._request(True)
        return requests.async.post(self.account.api_url, self.account.request_xml_template % {'body':self._input()}, **self.request_opts)

    @lazy_property
    def response(self):
        #return self._request(False)
        return requests.post(self.account.api_url, self.account.request_xml_template % {'body':self._input()}, **self.request_opts)

    def _request(self, async):
        obj = async and requests.async or requests
        return obj.post(self.account.api_url, self.account.request_xml_template % {'body':self._input()}, **self.request_opts)

    @lazy_property
    def answer(self):
        return self.process_response()



class GetListExchange(Exchange):
    def __init__(self, account, size=None, offset=None, request_opts=None, **opts):
        super(GetListExchange, self).__init__(account, request_opts, **opts)
        self.size = size
        self.offset = offset

    def process_response(self, response=None): # deal with exception thrown on empty lists
        try:
            return super(GetListExchange, self).process_response(response)
        except error.ApiError, err:
            if err.exception_id == 15:
                self._lazy_answer = ([],0)
                return self._lazy_answer
            raise

    @lazy_property
    def list_options_xml(self):
        if self.size is None and self.offset is None: return ''
        wrapper = '<listControl>%s</listControl>'
        innards = []
        if self.offset is not None: innards.append('<startFrom>%s</startFrom>'%(self.offset+1,))
        if self.size is not None: innards.append('<maximumNum>%s</maximumNum>'%(self.size,))
        return wrapper%(''.join(innards))

    def _input(self):
        return self._list_input() % self.list_options_xml

    def _list_input(self):
        raise NotImplementedError("this needs to be implemented in a derived class")

    def _answer(self, body_content):
        info = grab(find(body_content, '%s:matchingRecords'%self.__class__.ns), 'total', 'returned', 'startFrom', ns='serv')
        if int(info['startFrom'])-1 != self.offset:
            raise error.Error("The returned offset is different than the specified offset-- I would never expect this to happen")
        return (self._list_answer(body_content), int(info['total'])) 

    def _list_answer(self, body_content):
        raise NotImplementedError("this needs to be implemented in a derived class")



class BatchListExchange(object):
    def __init__(self, account, list_exchange_klass, key, batch_size=50, overlap=2, async=True):
        super(BatchListExchange, self).__init__()
        self.async = async
        self.account = account
        self.list_exchange_klass = list_exchange_klass
        self.key = key
        self.batch_size = batch_size
        self.overlap = overlap
        self.effective_batch_size = self.batch_size - self.overlap

    @lazy_property
    def items(self):
        items, total = self.list_exchange_klass(self.account, self.overlap or 1, 0).answer
        key_set = set([getattr(obj,self.key) for obj in items])
        batch_count = (total-self.batch_size-1) / self.effective_batch_size + 2
        exchanges = [self.list_exchange_klass(self.account, self.batch_size, i*self.effective_batch_size) for i in xrange(batch_count)]
        if self.async:
            responses = requests.async.map([e.request for e in exchanges])
            for e,r in zip(exchanges, responses): e.process_response(r) 
        for extra_items, total in [e.answer for e in exchanges]:
            if self.overlap and not extra_items:
                raise error.PagingSlippageError("Lost too many events during paging to be certain of the final result set.  You will need to try again.")
            if self.overlap and getattr(extra_items[0], self.key) not in key_set:
                raise error.PagingSlippageError("Too much movement in event list during paging to be certain of the final result set.  You will need to try again.")
            for obj in extra_items:
                if getattr(obj, self.key) not in key_set:
                    items.append(obj)
            key_set |= set(map(lambda obj: getattr(obj, self.key), extra_items))
        return items

    def process_batch_responses(self, batch_responses=None):
        if batch_responses is None:
            batch_responses = self.batch_responses
        if self.async:
            for e,r in zip(self.batch_exchanges, responses): e.process_response(r)
        for extra_items, total in [e.answer for e in self.batch_exchanges]:
            if self.overlap and not extra_items:
                raise error.PagingSlippageError("Lost too many events during paging to be certain of the final result set.  You will need to try again.")
            if self.overlap and getattr(extra_items[0], self.key) not in key_set:
                raise error.PagingSlippageError("Too much movement in event list during paging to be certain of the final result set.  You will need to try again.")
            for obj in extra_items:
                if getattr(obj, self.key) not in key_set:
                    self._items.append(obj)
            self.key_set |= set(map(lambda obj: getattr(obj, self.key), extra_items))
        return items

    def batch_responses(self):
        self.batch_exchanges




    def items
