# -*- coding: utf-8 -*-
import gtk
from xml.etree.ElementTree import ElementTree
from subprocess import Popen
from omnilib import notifier

class DockTable(gtk.Table):
    def __init__(self, color):
	self.color = color
	self.configTree = self.get_config()
	rows = int(self.configTree.findtext("rows"))
	columns = int(self.configTree.findtext("columns"))
        super(DockTable, self).__init__(rows, columns, homogeneous=True)
        self._add_launchers()
        self._add_notifiers()
	
	
    def _add_launchers(self):    
        #Pull launchers from XML config
	for launcher in self.configTree.findall("launcher"):
	    button = gtk.Button()
	    button.set_focus_on_click(False)
	    #setting button color is surprisingly complex
            cmap = button.get_colormap() 
            color = cmap.alloc_color(self.color)
            style = button.get_style().copy()
            style.bg[gtk.STATE_NORMAL] = color
            button.set_style(style)
            #Set icon
	    image  = gtk.Image()
	    image.set_from_file(launcher.findtext("icon"))
	    button.set_image(image)
	    command = launcher.findtext("exec")
	    #Connect click action and attach to table
	    button.connect("clicked", self.launch, command)
	    self.attach(button,
	                int(launcher.findtext("left_attach")),
	                int(launcher.findtext("right_attach")),
	                int(launcher.findtext("top_attach")),
	                int(launcher.findtext("bottom_attach")))
	                
	                
    def _add_notifiers(self):
	for configItem in self.configTree.findall("notifier"):
	    current = notifier.Notifier()
	    current.set_service(configItem.findtext("service"))
	    self.attach(current,
	                int(configItem.findtext("left_attach")),
	                int(configItem.findtext("right_attach")),
	                int(configItem.findtext("top_attach")),
	                int(configItem.findtext("bottom_attach")))
	                
	
    def get_free_cells(self):
	#This is the function from the awesome guy on StackOverflow.  
	#Thanks Geoff!
	table = self
        free_cells = set([(x,y) for x in range(table.props.n_columns) for y in range(table.props.n_rows)])
	def func(child):
	    (l,r,t,b) = table.child_get(child, 'left-attach','right-attach','top-attach','bottom-attach')
	    used_cells = set([(x,y) for x in range(l,r) for y in range(t,b)])
	    free_cells.difference_update(used_cells)
	table.foreach(func)
        return free_cells
        
        
    def launch(self, button, command):
	self.running_process = Popen([command])
    
    def get_config(self):
    	etree = ElementTree()
    	config = etree.parse("config/docktable.xml")
    	return config
    