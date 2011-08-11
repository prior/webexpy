try:
    from lxml import etree as ET
    print("running with lxml")
except ImportError:
    try:
        import xml.etree.cElementTree as ET
        print("running with cElementTree")
    except ImportError:
        try:
            import xml.etree.ElementTree as ET
            print("running with ElementTree")
        except ImportError:
            print("Failed to import any ElementTree library!")


XSI_URI='{http://www.w3.org/2001/XMLSchema-instance}'
class WebExRequestBuilder(object):
    """Builds an XML file based on the WebExRequest object"""
    def __init__(self, head, body):
        self.header=head
        self.body= None

    def getBodyXml(self):
        NSMAP= {'xsi':'http://www.w3.org/2001/XMLSchema-instance'}
        self.body= ET.Element('body', nsmap=NSMAP)
        return self.body

    def getHeaderXml(self):
        xheader=self.header

        head= ET.Element('header')
        securitycontext= ET.SubElement(head, "securityContext")
        webid= ET.SubElement(securitycontext, "webExID")
        webid.text= xheader.webexId
        webpass= ET.SubElement(securitycontext, "password")
        webpass.text=xheader.password
        if not xheader.siteId==None:
            siteid.text= ET.SubElement(securitycontext,"siteID")
            siteid.text= xheader.siteId
        sitename= ET.SubElement(securitycontext, "siteName")
        sitename.text= xheader.siteName
        email= ET.SubElement(securitycontext, "email")
        email.text= xheader.email
        return head
       
    def getRequestXml(self):
        xml= ET.tostring(self.getRequestXmlTree(),encoding= 'UTF-8')
        return xml

    def getRequestXmlTree(self):
        """Returns ElementTree representation of the XML (can be used for testing purposes)"""
        NSMAP={'serv':"http://www.webex.com/schemas/2002/06/service"} 
        root = ET.Element('{http://www.webex.com/schemas/2002/06/service}message', nsmap=NSMAP)
        root.append(self.getHeaderXml())
        root.append(self.getBodyXml())
        return root

