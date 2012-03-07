class Error(ValueError): pass

class PagingSlippageError(Error): pass

class InvalidAccount(Error): pass

class RequestError(Error):
    def __init__(self, request, err_str=None):
        super(RequestError, self).__init__(err_str or str(request.url))
        self.request = request

class TimeoutError(RequestError): 
    def __init__(self, request, err_str=None):
        super(TimeoutError, self).__init__(request, err_str or 'Exceeded %ss timeout'%(request.timeout or '?'))
        self.request = request

class ResponseError(RequestError):
    def __init__(self, response, err_str=None):
        super(ResponseError, self).__init__(response.request, err_str or str(response.status_code))
        self.response = response

class ApiError(ResponseError):
    def __init__(self, response, success, exception_id, reason, value, gsb_status, err_str=None):
        super(ApiError, self).__init__(response, err_str or reason)
        self.success = success
        self.exception_id = exception_id
        self.reason = reason
        self.value = value
        self.gsb_status = gsb_status

    def __str__(self):
        return "%s: %s [success=%s, gsb_status=%s, value=%s]\n%s" % (self.exception_id, self.reason, self.success, self.gsb_status, self.value, self.request.data)

class ParseError(ResponseError):
    def __init__(self, response, err_str=None):
        super(ParseError, self).__init__(response, str(response.content))


