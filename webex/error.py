class Error(ValueError): pass
class TimeoutError(Error): 
    def __init__(self, timeout):

    timeout_valuepass



class InvalidAccount(Error): pass

class ApiError(Error):
    def __init__(self, exception_id, reason):
        self.exception_id = exception_id
        self.reason = reason
class UnknownEventError(ApiError): pass

        except requests.exceptions.Timeout:
            self._reraise(error.TimeoutError(options['timeout']))
        except requests.exceptions.RequestException:
            self._reraise(error.RequestError())
        if result.status_code != 200:
            raise error.ServerError(result)
        try:
            root = etree.fromstring(result.content)
        except:
            reraise(error.ParseError(result.content))
 
