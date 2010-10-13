# -*- coding: utf-8 -*-
import gtk
from xml.etree.ElementTree import ElementTree
from subprocess import Popen
from omnilib import notifier

class DockTable(gtk.Table):
    def __init__(self, color):
	self.color = color
	self.configTree = self.get_config()
	self.notifiers = {}
	rows = int(self.configTree.findtext("rows"))
	columns = int(self.configTree.findtext("columns"))
        super(DockTable, self).__init__(rows, columns, homogeneous=True)
        self._add_launchers()
        self._add_notifiers()
	
	
    def _add_launchers(self):    
        #Pull launchers from XML config
	for element in self.configTree.findall("launcher"):
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
	    image.set_from_file(element.findtext("icon"))
	    button.set_image(image)
	    command = element.findtext("exec")
	    #Connect click action and attach to table
	    button.connect("clicked", self.launch, command)
	    self._add_to_table(element, button)
	    
	                    
    def _add_notifiers(self):
	for element in self.configTree.findall("notifier"):
	    noteObject = notifier.Notifier()
	    service = element.findtext("service")
	    noteObject.set_service(service)
	    #grab attachment info, convert to integer, attach
	    self._add_to_table(element, noteObject)
	    self.notifiers[service] = noteObject
	 
	 
    def _add_to_table(self, element, widget):
	coords = map(int, map(element.findtext, ("left_attach", "right_attach", "top_attach", "bottom_attach")))
	self.attach(widget, *coords)
	                
	                
    def update_notifier(self, service, value):
	current = self.notifiers[service]
	current.set_badge(value)
	                
	
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
    