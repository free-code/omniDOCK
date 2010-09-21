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
	window = self.find("window")
	
	#Make sure decorated property is set to true/false
        if (window.findtext("decorated") == "True"):
	    pass
	elif (window.findtext("decorated") == "False"):
	    pass
	else:
	    message = "'decorated' property must be True or False."
	    self._on_err(TypeError, message)
        
        #Verify that height and width are integerish
        try:
	    int(self.findtext("height"))
	except:
	    message = "Somehow, 'height' property is not an integer."
	    self.on_err(TypeError, message)
	try:
	    int(self.findtext("width"))
	except:
	    message = "Somehow, 'width' property is not an integer."
	    self.on_err(TypeError, message)
        
        
    def _on_err(self, errType, message):
	raise errType, message
        print "Check %s" % self.configFile
	
		