# -*- coding: utf-8 -*-
import gtk
import PythonMagick
import random


class Notifier(gtk.Image):
    def __init__(self):
	super(Notifier, self).__init__()
	self.service = None
        self.badgeValue = None
    
    def set_service(self, service):
	self.service = service
	self._set_icon(service)
    
    
    def set_badge(self, value):
	self.badgeValue = value
	print "Badge for %s is now" % self.service, value
    
    def _set_icon(self, service):
	if service == "facebook":
	    filename = "bluefish.png"
	    

	magickImage = PythonMagick.Image(filename)
	#magickImage.rotate(15)
	magickImage.fillColor('#FFFFFF')
	magickImage.annotate("beets", PythonMagick._PythonMagick.GravityType.SouthGravity)
	tmpFile = "/tmp/temp" + str(random.randint(1,10000))
	magickImage.write(tmpFile)
	
	print dir(magickImage.annotate)
	
	self.set_from_file(tmpFile)
	
    
