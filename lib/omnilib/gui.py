# -*- coding: utf-8 -*-
import gtk
import docktable


class OmniDOCKGUI(gtk.Window):
    def __init__(self):
	#The window class is only a container for the table
	super(OmniDOCKGUI, self).__init__(gtk.WINDOW_TOPLEVEL)
	self.configTree = None
	self.connect('destroy', gtk.main_quit)
	self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)

	
    def add_docktable(self):
	#Add the table to the window
	color = self.configTree.findtext("window/bg")
	self.table = docktable.DockTable(color)
	self.add(self.table)
	self.set_focus(self.table)


    def apply_strut(self, align):
	top = self.get_toplevel().window
	if align == "left":
	    top.property_change("_NET_WM_STRUT", "CARDINAL", 32, 
	                        gtk.gdk.PROP_MODE_REPLACE, [self.width, 0, 0, 0])
	elif align == "right":
	    top.property_change("_NET_WM_STRUT", "CARDINAL", 32, 
	                        gtk.gdk.PROP_MODE_REPLACE, [0, self.width, 0, 0])
	else:
	    raise ValueError("Invalid alignment.  Defaulting to 'left'")


    def apply_config(self, configTree):
	self.configTree = configTree
	#Dock geometry
	self.height = int(configTree.findtext("window/height"))
        self.width = int(configTree.findtext("window/width"))
	self.set_size_request(self.width, self.height)
	#Apply background color
        color = gtk.gdk.color_parse(configTree.findtext("window/bg"))
	self.modify_bg(gtk.STATE_NORMAL, color)
	#Hide/show desktop environment titlebar and buttons
	self.set_decorated(False)
	#Set translucency
	opacity = float(configTree.findtext("window/opacity"))
	self.set_opacity(opacity)
	#Run alignment method to place dock on screen
        align = configTree.findtext("window/align")
        self.align_to(align)
        #And finally add the table (where the magic happens)
        self.add_docktable()
        self.show_all()
        self.apply_strut(align)
         

    def align_to(self, alignment):
        holder = gtk.gdk.display_get_default()
	screen = holder.get_default_screen()
	screenH = screen.get_height()
	screenW = screen.get_width()
	# left ypos available in case we decide to implement vertical offsets
	if alignment == "right":
            xpos = screenW - int(self.configTree.findtext("window/width"))
            ypos = 0
        elif alignment == "left":
	    #self.get_root_window().property_change("_NET_WM_STRUT", "CARDINAL", 32, gtk.gdk.PROP_MODE_REPLACE, [50, 0, 0, 0])
	    xpos = 0
	    ypos = 0
	else:
	    raise ValueError("Invalid alignment.  Defaulting to 'left'")
	    xpos = 0
	    ypos = 0
	self.move(xpos,ypos)
	    