import requests
import requests.async
from .xutils import find, nfind_str, nfind_int, reraise, lazy_property, grab
from . import error
from lxml import etree

def batch_action(exchange_klass, items):
    exchanges = [exchange_klass(item) for item in items]
    return [e.process_response(r) for e,r in zip(exchanges, requests.async.map([e.request for e in exchanges]))]

def batch_bulk_action(bulk_exchange_klass, items, batch_size=50):
    start_pos = 0
    exchanges = []
    while start_pos < len(items):
        exchanges.append(bulk_exchange_klass(items[start_pos:start_pos+batch_size]))
        start_pos += batch_size
    return [r for sublist in [e.process_response(r) for e,r in zip(exchanges, requests.async.map([e.request for e in exchanges]))] for r in sublist]

# This class is the way it is to allow for synchronous and asynchronous calling possibilities (though after building things this way, it appears that webex allows zero-to-none concurrency on a single account domain-- fuck)
class Exchange(object):
    def __init__(self, account, request_opts=None, **opts):
        super(Exchange, self).__init__()
        self.account = account
        self.request_opts = {'timeout':100}
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
        except requests.exceptions.Timeout as err:
            reraise(error.TimeoutError(self.request, err=err))
        except requests.exceptions.RequestException as err:
            if response is None or response.status_code==0:
                reraise(error.RequestError(self.request, 'unknown error', err=err))
            else:
                reraise(error.ResponseError(response, err=err))
        if response.status_code != 200:
            raise error.ResponseError(response, 'unexpected status response: %s (%s)' % (response.status_code, response.content))
        try:
            root = etree.fromstring(response.content)
        except BaseException as err:
            reraise(error.ParseError(response, err=err))
        if self.opts.get('debug'): print etree.tostring(etree.fromstring(response.content), pretty_print=True)
        resp = find(root, 'serv:header', 'serv:response')
        success = find(resp, 'serv:result').text.lower() == "success"
        gsb_status = nfind_str(resp, 'serv:gsbStatus')
        exception_id = nfind_int(resp, 'serv:exceptionID')
        reason = nfind_str(resp, 'serv:reason')
        value = nfind_str(resp, 'serv:value')
        if not success: 
            if exception_id==30001:
                raise error.InvalidUsernameError(response, success, exception_id, reason, value, gsb_status, info='be careful-- too many of these and the account will be locked')
            elif exception_id==30002:
                raise error.InvalidPasswordError(response, success, exception_id, reason, value, gsb_status, info='be careful-- too many of these and the account will be locked')
            raise error.ApiError(response, success, exception_id, reason, value, gsb_status)
        try:
            self._lazy_answer = self._process_xml(find(root, 'serv:body', 'serv:bodyContent'))
            return self._lazy_answer
        except Exception as err:
            reraise(error.ParseError(response, err=err))

    def _process_xml(self, body_content):
        raise NotImplementedError("this needs to be implemented in a derived class")

    def _input(self):
        raise NotImplementedError("this needs to be implemented in a derived class")
    
    @lazy_property
    def request(self):
        return self._build_request(True)

    @lazy_property
    def response(self):
        return self._build_request(False)

    def _build_request(self, async):
        obj = async and requests.async or requests
        xml = self.account.request_xml_template % {'body':self._input()}
        return obj.post(self.account.api_url, unicode(xml).encode('utf8'), **self.request_opts)

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
        except error.ApiError as err:
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

    def _process_xml(self, body_content):
        info = grab(find(body_content, '%s:matchingRecords'%self.__class__.ns), 'total', 'returned', 'startFrom', ns='serv')
        if int(info['startFrom'])-1 != self.offset:
            raise error.Error("The returned offset is different than the specified offset-- I would never expect this to happen")
        return (self._process_list_xml(body_content), int(info['total']))

    def _process_list_xml(self, body_content):
        raise NotImplementedError("this needs to be implemented in a derived class")


class BatchListExchange(object):
    def __init__(self, list_exchange_klass, arg, key, batch_size=50, overlap=2, async=True):
        super(BatchListExchange, self).__init__()
        self.async = async
        self.arg = arg
        self.list_exchange_klass = list_exchange_klass
        self.key = key
        self.batch_size = batch_size
        self.overlap = overlap
        self.effective_batch_size = self.batch_size - self.overlap

    @lazy_property
    def items(self):
        batch_responses=None
        if self.async:
            batch_responses = requests.async.map(self.batch_requests)
        return self.process_batch_responses(batch_responses)

    def process_batch_responses(self, batch_responses=None):
        if self.async:
            for e,r in zip(self.batch_exchanges, batch_responses): e.process_response(r)
        for extra_items, total in [e.answer for e in self.batch_exchanges]:
            if self.overlap and not extra_items:
                raise error.PagingSlippageError("Lost too many events during paging to be certain of the final result set.  You will need to try again.")
            if self.overlap and getattr(extra_items[0], self.key) not in self._dict:
                raise error.PagingSlippageError("Too much movement in event list during paging to be certain of the final result set.  You will need to try again.")
            for obj in extra_items: self._add_item(obj)
        self._lazy_items = self._items
        return self._items

    @lazy_property
    def batch_requests(self):
        return [e.request for e in self.batch_exchanges]

    def _add_item(self, obj):
        if getattr(obj, self.key) in self._dict:
            self._dict[getattr(obj,self.key)].merge(obj)
        else:
            self._items.append(obj)
            self._dict[getattr(obj,self.key)] = obj

    @lazy_property
    def batch_exchanges(self):
        self._items=[]
        self._dict={}
        for obj in self.initial_exchange.answer[0]: self._add_item(obj)
        batch_count = (self.initial_exchange.answer[1]-self.batch_size-1) / self.effective_batch_size + 2
        return [self.list_exchange_klass(self.arg, self.batch_size, i*self.effective_batch_size) for i in xrange(batch_count)]
        
    @lazy_property
    def initial_exchange(self):
        return self.list_exchange_klass(self.arg, self.overlap or 1, 0)



class ParallelBatchListExchange(object):
    def __init__(self, batch_list_exchanges):
        super(ParallelBatchListExchange, self).__init__()
        self.batch_list_exchanges = batch_list_exchanges
        self.async = all([ble.async for ble in batch_list_exchanges])
        self.key = batch_list_exchanges[0].key

    @lazy_property
    def items(self):
        if self.async:
            responses = requests.async.map([ble.initial_exchange.request for ble in self.batch_list_exchanges])
            for ble,r in zip(self.batch_list_exchanges, responses):
                ble.initial_exchange.process_response(r)
            batch_requests = [ble.batch_requests for ble in self.batch_list_exchanges]
            sizes = [len(br) for br in batch_requests]
            reqs = [r for sublist in batch_requests for r in sublist]
            responses = requests.async.map(reqs)
            batch_responses = []
            for s in sizes:
                batch_responses.append(responses[0:s])
                del responses[0:s]
            for ble, br in zip(self.batch_list_exchanges, batch_responses):
                ble.process_batch_responses(br)

        items_hash = dict((getattr(item, self.key), item) for item in self.batch_list_exchanges[0].items)
        for e in self.batch_list_exchanges[1:]:
            for item in e.items:
                if items_hash.get(getattr(item, self.key)):
                    items_hash[getattr(item, self.key)].merge(item)
                else:
                    items_hash[getattr(item, self.key)] = item
        items = items_hash.values()
        items.sort()
        return items

