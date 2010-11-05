# -*- coding: utf-8 -*-
import gtk
import PythonMagick
import random


class Notifier(gtk.Image):
    def __init__(self):
	super(Notifier, self).__init__()
	self.service = None
        self.badgeValue = None
        
    def update(self, service, value):
	filename = self._get_service_icon(service)
	magickImage = PythonMagick.Image(filename)
	#magickImage.rotate(15)
	magickImage.sample(PythonMagick._PythonMagick.Geometry(48, 48))
	magickImage.fillColor('#FFFFFF')
	magickImage.annotate(str(value), PythonMagick._PythonMagick.GravityType.SouthGravity)
	tmpFile = "/tmp/temp" + str(random.randint(1,10000))
	magickImage.write(tmpFile)
	self.set_from_file(tmpFile)
	
    
    def _get_service_icon(self, service):
        if service == "facebook":
	    filename = "images/facebook.png"
	else:
	    filename = "bluefish.png"
	return filename