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
	    button.connect("button_press_event", self.launcher_right_clicked)
	    self._add_to_table(element, button)
	    
	                    
    def _add_notifiers(self):
	for element in self.configTree.findall("notifier"):
	    noteObject = notifier.Notifier()
	    service = element.findtext("service")
	    noteObject.update(service, 0)
	    #grab attachment info, convert to integer, attach
	    self._add_to_table(element, noteObject)
	    self.notifiers[service] = noteObject
	 
	 
    def _add_to_table(self, element, widget):
	coords = map(int, map(element.findtext, ("left_attach", "right_attach", "top_attach", "bottom_attach")))
	self.attach(widget, *coords)
	
    def add_gizmo(self,giz):
	#Faking the intelligent placement for testing
	gizmo = giz[0]
	height = giz[1][0]
	width = giz[1][1]
	self.attach(gizmo, 0, 4, 5, 8)
	                
	                
    def update_notifier(self, service, value):
	current = self.notifiers[service]
	current.update(service, value)
	                
	
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
	print button
	self.running_process = Popen([command])
    
    def get_config(self):
    	etree = ElementTree()
    	config = etree.parse("config/docktable.xml")
    	return config
    
    
    def launcher_right_clicked(self, button, event):
	if(event.button != 3): 
            return False 
        menu = gtk.Menu()
        item1 = gtk.MenuItem("I'm a Cucumber")
        item1.connect("activate", self.add_launcher_gui)
        menu.add(item1)
        
        menu.append(gtk.MenuItem("Me too"))
        menu.show_all()
        
        menu.popup(None, None, None, event.button, event.time)
   

    def add_launcher_gui(self, data):
        win = gtk.Window()
        vbox = gtk.VBox()
        entry = gtk.Entry()
        label = gtk.Label("Enter command to launch")
        button = gtk.Button("OK")
        button.connect("clicked", self.launcher_gui_cb, win, entry)
        vbox.pack_start(label)
        vbox.pack_start(entry)
        vbox.pack_end(button)
        win.add(vbox)
        win.show_all()
        
    def launcher_gui_cb(self, data, win, entry):
	result = entry.get_text()
	print result
	win.hide_all()