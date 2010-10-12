# -*- coding: utf-8 -*-
import gtk

class Notifier(gtk.Image):
    def __init__(self):
	self.service = None
        self.badgeValue = None
    
    def set_service(self, service):
	self.service = service
	self._set_icon(service)
    
    
    def set_badge(self, value):
	self.badgeValue = value
    
    def _set_icon(self, service):
	if service == "facebook":
	    filename = "facebook.png"
	self.set_from_file(filename)
	
    
