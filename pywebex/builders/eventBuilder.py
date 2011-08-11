import webexBuilder as build

class CreateEvent(build.WebExRequestBuilder):
    def __init__(self):
        pass

class GetEvent(build.WebExRequestBuilder):
    def __init__(self, head, rdict):
        self.header= head
        self.rdict=rdict

    def getBodyXml(self):
        body=super(GetEvent,self).getBodyXml()
        bodycontent=build.ET.SubElement(body,"bodyContent")
        bodycontent.set(build.XSI_URI+"type", "event:getEvent")
        sessionkey= build.ET.SubElement(bodycontent, "sessionKey")
        sessionkey.text=self.rdict['key']
        return body

class setEvent(build.WebExRequestBuilder):
    def __init__(self):
        pass 
