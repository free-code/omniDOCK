# -*- coding: utf-8 -*-
import gtk
import docktable

class OmniDOCKGUI(gtk.Window):
    def __init__(self, configTree):
	super(OmniDOCKGUI, self).__init__()
        height = int(configTree.findtext("window/height"))
        width = int(configTree.findtext("window/width"))
	self.set_size_request(width, height)
	self.add_docktable()
	self.connect('destroy', gtk.main_quit)
	self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("black"))
	self.set_decorated(False)
	opacity = float(configTree.findtext("window/opacity"))
	self.set_opacity(opacity)
	self.set_keep_above(True)
	#self.set_position(gtk.WIN_POS_RIGHT)
	#self.set_gravity(gtk.gdk.GRAVITY_NORTH_WEST)
	xpos = int(configTree.findtext("window/xpos"))
	ypos = int(configTree.findtext("window/ypos"))
	self.move(xpos,ypos)
	#Can't seem to figure out how to align to right side
	
    def add_docktable(self):
	print "adding docktable"
	table = docktable.DockTable()
	self.add(table)
	
    def show_window(self):
	self.show_all()
	gtk.main()
	
    


	