from lxml import objectify
from lxml import etree

class WebExResponseParser(object):
    """Parser returns tree representation of the WebExResponse"""
    def __init__(self, x, type):
        self.xml=x
        self.stype= type

    def getWebExResponse(self):
        response= objectify.fromstring(self.xml)
        return response



###For validation...not yet implemented####    
    def getSchema(self, type):
        schema = etree.XMLSchema(file=file(getLocation(type)))        
        return schema

    def getLocation(self, type):
        location= '../schemas/service/{0}/{0}.xsd' % type
        return location

    def getParser(self):
        parser= objectify.makeparser(schema= getSchema(self.stype))
        return parser
    
