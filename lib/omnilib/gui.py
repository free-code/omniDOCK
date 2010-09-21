# -*- coding: utf-8 -*-
import gtk
import docktable

class OmniDOCKGUI(gtk.Window):
    def __init__(self):
	super(OmniDOCKGUI, self).__init__()
	self.configTree = None
	self.connect('destroy', gtk.main_quit)
	
    def add_docktable(self):
	table = docktable.DockTable()
	self.add(table)


    def show_window(self):
	self.show_all()
	gtk.main()


    def apply_config(self, configTree):
	self.configTree = configTree
	#Dock geometry
	height = int(configTree.findtext("window/height"))
        width = int(configTree.findtext("window/width"))
	self.set_size_request(width, height)
	#Apply background color
        color = gtk.gdk.color_parse(configTree.findtext("window/bg"))
	self.modify_bg(gtk.STATE_NORMAL, color)
	#Hide/show desktop environment titlebar and buttons
	self.set_decorated(False)
	#Set translucency
	opacity = float(configTree.findtext("window/opacity"))
	self.set_opacity(opacity)
	#Run alignment method to place dock on screen
        self.align_to(configTree.findtext("window/align"))
        #And finally add the table (where the magic happens)
        self.add_docktable()
         

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
	    xpos = 0
	    ypos = 0
	else:
	    raise "Invalid alignment: %s.  Defaulting to 'left'"
	    xpos = 0
	    ypos = 0
	self.move(xpos,ypos)
	    