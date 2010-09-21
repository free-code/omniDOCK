# -*- coding: utf-8 -*-
from xml.etree.ElementTree import ElementTree

class DockConfig(ElementTree):
    def load(self):
    	self.parse("config/dockconfig.xml")
    	
    def save(self):
	self.write("config/dockconfig.xml")