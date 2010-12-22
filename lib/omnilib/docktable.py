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
	print "Got click signal"
	if(event.button != 3): 
            return False 
        menu = gtk.Menu()
        menu.set_title("Launcher Options")
        menu.add(gtk.MenuItem("I'm a Cucumber"))
        menu.append(gtk.MenuItem("Me too"))
        menu.show_all()
        menu.popup(None, None, self.menu_position, event.button, event.time, button)

        
    def menu_position(self, menu, button):
        screen = button.get_screen()
        monitor = screen.get_monitor_at_window(button.window)
        monitor_allocation = screen.get_monitor_geometry(monitor)

        x, y = button.window.get_origin()
        x += button.allocation.x
        y += button.allocation.y

        menu_width, menu_height = menu.size_request()

        if x + menu_width >= monitor_allocation.width:
            x -= menu_width - button.allocation.width
        elif x - menu_width <= 0:
            pass
        else:
            if x <= monitor_allocation.width * 3 / 4:
                pass
            else:
                x -= menu_width - button.allocation.width
    
        if y + button.allocation.height + menu_height >= monitor_allocation.height:
            y -= menu_height
        elif y - menu_height <= 0:
            y += button.allocation.height
        else:
            if y <= monitor_allocation.height * 3 / 4:
                y += button.allocation.height
            else:
                y -= menu_height
    
        return (x, y, False)
        
        
        