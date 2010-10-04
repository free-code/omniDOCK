# -*- coding: utf-8 -*-
from xml.etree.ElementTree import ElementTree

class DockConfig(ElementTree):
    def __init__(self):
	self.configFile = "config/dockconfig.xml"
	
	
    def load(self):
    	self.parse(self.configFile)
        self._verify()
    	
    	
    def save(self):
	self._verify()
	self.write(self.configFile)
	
	
    def _verify(self):
	#Made it this way because the assignment succeeds even if there's
	#no 'window' node in the config - it just assigns as None.  
	try:
	    window = self.find("window")
	    assert window != None
	except:
	    message = "'window' node not found in config"
	    self._on_err(AttributeError, message)
	    
	#Same here
	try:
	    dec = window.findtext("decorated")
	    assert dec != None
	except:
	    message = "'decorated' property not found in config"
	    self._on_err(AttributeError, message)
	#Make sure decorated property is set to true/false
        if dec != "True" and dec != "False":
            message = "'decorated' property must be 'True' or 'False'. Got '%s'" % dec
            self._on_err(TypeError, message)
        
        #Verify that height and width are integerish
        for attr in ("height", "width"):
	    try:
		int(window.findtext(attr))
	    except ValueError as err:
		message = "invalid data type for '%s' property in config" % attr
		self._on_err(err, message)
	    except TypeError as err:
		#It seems odd that failure to find a node causes a typeerror,
		#but that's what happens in testing.  
		message = "'%s' property not found in config" % attr
		self._on_err(err, message)
		
        
    def _on_err(self, errType, message):
	raise errType, message
        
	
		