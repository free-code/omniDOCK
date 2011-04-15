# -*- coding: utf-8 -*-
import gtk
from xml.etree.ElementTree import ElementTree
from subprocess import Popen
from omnilib import notifier, addlauncherdialog


class DockTable(gtk.Table):
    def __init__(self, color):
        self.color = color
	self.configTree = self.get_config()
	self.notifiers = {}
	rows = int(self.configTree.findtext("rows"))
	columns = int(self.configTree.findtext("columns"))
        super(DockTable, self).__init__(rows, columns, homogeneous=True)
        
        self._add_saved_launchers()
        #self._add_notifiers()
	
	
    def _add_saved_launchers(self):
        #Pull launchers from XML config
	for element in self.configTree.findall("launcher"):
	    iconPath = element.findtext("icon")
            command = element.findtext("exec")
            name = element.findtext("name")
	   
            coords = map(int, map(element.findtext, ("left_attach", "right_attach", "top_attach", "bottom_attach")))
	    details = {"name": name, "exec": command, "attach": coords, "icon":iconPath}
            self._add_single_launcher(details)


    def _add_single_launcher(self, details):
        image  = gtk.Image()
        image.set_from_file(details["icon"])
        newButton = gtk.Button()
        newButton.set_focus_on_click(False)
	cmap = newButton.get_colormap()
        color = cmap.alloc_color(self.color)
        style = newButton.get_style().copy()
        style.bg[gtk.STATE_NORMAL] = color
        newButton.set_style(style)
	newButton.set_image(image)
        newButton.connect("clicked", self.launch, details["exec"])
	newButton.connect("button_press_event", self.launcher_right_clicked)
        print "Adding", details
        self.attach(newButton, *details["attach"])
        self.show_all()

    def _add_notifiers(self):
	for element in self.configTree.findall("notifier"):
	    noteObject = notifier.Notifier()
	    service = element.findtext("service")
	    noteObject.update(service, 0)
	    #grab attachment info, convert to integer, attach
	    self._add_to_table(element, noteObject)
	    self.notifiers[service] = noteObject
	 
	 
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
        item1 = gtk.MenuItem("Add a Launcher")
        item1.connect("activate", self._show_add_launcher_gui)
        menu.add(item1)
        
        menu.append(gtk.MenuItem("DUMMY Remove Launcher"))
        menu.show_all()
        
        menu.popup(None, None, None, event.button, event.time)
   

    def _show_add_launcher_gui(self, data):
        diag = addlauncherdialog.AddLauncherDialog(self._add_single_launcher)
        diag.show()
        
    def launcher_gui_cb(self, data, win, entry):
	result = entry.get_text()
	print result
	win.hide_all()