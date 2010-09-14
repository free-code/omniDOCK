# -*- coding: utf-8 -*-
import gtk
from xml.etree.ElementTree import ElementTree

class DockTable(gtk.Table):
    def __init__(self):
	
	self.configTree = self.get_config()
	rows = int(self.configTree.findtext("rows"))
	columns = int(self.configTree.findtext("columns"))
        #self.set_homogeneous(True)
        super(DockTable, self).__init__(rows, columns, homogeneous=True)
        self.add_launchers()
	#return self
	
    def add_launchers(self):
	for launcher in self.configTree.findall("launcher"):
	    print "found a launcher"
	    button = gtk.Button()
	    image  = gtk.Image()
	    image.set_from_file(launcher.findtext("icon"))
	    button.set_image(image)
	    self.attach(button,
	                int(launcher.findtext("left_attach")),
	                int(launcher.findtext("right_attach")),
	                int(launcher.findtext("top_attach")),
	                int(launcher.findtext("bottom_attach")))
	
    def get_free_cells(self):
	table = self
        free_cells = set([(x,y) for x in range(table.props.n_columns) for y in range(table.props.n_rows)])
	def func(child):
	    (l,r,t,b) = table.child_get(child, 'left-attach','right-attach','top-attach','bottom-attach')
	    used_cells = set([(x,y) for x in range(l,r) for y in range(t,b)])
	    free_cells.difference_update(used_cells)
	table.foreach(func)
        return free_cells
    
    def get_config(self):
	print "loading config"
    	etree = ElementTree()
    	config = etree.parse("config/docktable.xml")
    	return config
    