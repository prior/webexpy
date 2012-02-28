class Error(ValueError): pass
class InvalidAccount(Error): pass

class ApiError(Error):
    def __init__(self, exception_id, reason):
        self.exception_id = exception_id
        self.reason = reason
class UnknownEventError(ApiError): pass

 
