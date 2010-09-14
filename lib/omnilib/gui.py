# -*- coding: utf-8 -*-
import gtk

class OmniDOCKGUI(gtk.Window):
    def __init__(self, configTree):
	super(OmniDOCKGUI, self).__init__()
        height = int(configTree.findtext("window/height"))
        width = int(configTree.findtext("window/width"))
	self.set_size_request(width, height)
	
    def show_window(self):
	self.show()
	gtk.main()


	