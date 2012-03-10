from lxml import etree

class Error(ValueError):
    def __init__(self, info=None, err=None):
        super(Error, self).__init__(str(info or err))
        self.wrapped_error = err
        self.extra_info = info

    @property
    def wrapped_error_str(self):
        if self.wrapped_error:
            return '[ %s: %s ]' % (str(self.wrapped_error.__class__).split("'")[1],str(self.wrapped_error))
        return None

    def __str__(self):
        return ('%s %s' % (self.extra_info, self.wrapped_error_str or '')).strip()
    
class PagingSlippageError(Error): pass
class InvalidAccount(Error): pass

class RequestError(Error):
    def __init__(self, request, info=None, err=None):
        super(RequestError, self).__init__(info, err)
        self.request = request

    def __str__(self):
        return "%s\n%s" % (super(RequestError, self).__str__(), self.request.url)

class TimeoutError(RequestError): 
    def __str__(self):
        return "Exceeded %ss timeout! %s" % (self.request.timeout or '?', super(TimeoutError, self).__str__())

class ResponseError(RequestError):
    def __init__(self, response, info=None, err=None):
        super(ResponseError, self).__init__(response.request, info, err)
        self.response = response

    def __str__(self):
        return "%s %s" % (super(ResponseError, self).__str__(), str(self.response.status_code))

class ApiError(ResponseError):
    def __init__(self, response, success, exception_id, reason, value, gsb_status, info=None, err=None):
        super(ApiError, self).__init__(response, info, err)
        self.success = success
        self.exception_id = exception_id
        self.reason = reason
        self.value = value
        self.gsb_status = gsb_status

    def __str__(self):
        return "%s: %s [success=%s, gsb_status=%s, value=%s]\n%s\n%s" % (self.exception_id, self.reason, self.success, self.gsb_status, self.value, super(ApiError, self).__str__(), self.request.data)

class InvalidUsernameError(ApiError): pass
class InvalidPasswordError(ApiError): pass

class ParseError(ResponseError):
    def __init__(self, response, info=None, err=None):
        super(ParseError, self).__init__(response, info, err)

    def __str__(self):
        return "%s\n%s" % (super(ResponseError, self).__str__(), etree.tostring(etree.fromstring(str(self.response.content)), pretty_print=True))


