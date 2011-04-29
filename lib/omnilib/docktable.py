# -*- coding: utf-8 -*-
import sys; sys.path += ['lib/', 'config/']
import contentconfig
import gtk
import xml.etree.ElementTree as ETree
from subprocess import Popen
from omnilib import notifier, addlauncherdialog
from operator import itemgetter, attrgetter


class DockTable(gtk.Table):
    def __init__(self, color):
        self.color = color
	self.configTree = contentconfig.ContentConfig()
        self.configTree.load()
	self.notifiers = {}
	rows = int(self.configTree.findtext("rows"))
	columns = int(self.configTree.findtext("columns"))
        super(DockTable, self).__init__(rows, columns, homogeneous=True)
        
        try:
            self._add_saved_launchers()
        except Exception as err:
            print err
            print "Failed to load launchers from config file"
        #self._add_notifiers()
	
	
    def _add_saved_launchers(self):
        #Pull launchers from XML config
	for element in self.configTree.findall("launcher"):
	    iconPath = element.findtext("icon")
            command = element.findtext("exec")
            name = element.findtext("name")
	   
            coords = map(int, map(element.findtext, ("left_attach", "right_attach", "top_attach", "bottom_attach")))
	    details = {"name": name, "exec": command,
            "left_attach": coords[0],
            "right_attach": coords[1],
            "top_attach": coords[2],
            "bottom_attach": coords[3],
            "icon":iconPath,
            "auto": False}
            self._add_single_launcher(details, isnew=False)


    def _add_single_launcher(self, details, isnew):
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
        spaces = []
        if details["auto"] == "true":
            open_spaces=self.get_free_cells()
            for i in open_spaces:
                spaces.append(i)
                #print sorted_spaces
            sorted_spaces = sorted(spaces)
            first_spot = sorted_spaces[0]
            details["left_attach"] = first_spot[1]
            details["right_attach"] = first_spot[1] + 1
            details["top_attach"] = first_spot[0]
            details["bottom_attach"] = first_spot[0] + 1
            

        self.attach(newButton, details["left_attach"],
                               details["right_attach"],
                               details["top_attach"],
                               details["bottom_attach"])
        if isnew == True:
          self._add_launcher_to_config(details)
        self.show_all()
        

    def _add_launcher_to_config(self, details):
        #Get the root node
        for x in details.keys():
            print x, details[x]
        rootElement = self.configTree.getroot()
        launcherElement = ETree.Element("launcher")
        for elem in details.keys():
            if type(details[elem]) is int:
                details[elem] = str(details[elem])
            thisNode = ETree.SubElement(launcherElement, elem)
            thisNode.text = details[elem]
        ETree.dump(rootElement)
        rootElement.append(launcherElement)
        self.configTree.save()

	 
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
        free_cells = set([(y,x) for x in range(table.props.n_columns) for y in range(table.props.n_rows)])
	def func(child):
	    (l,r,t,b) = table.child_get(child, 'left-attach','right-attach','top-attach','bottom-attach')
	    used_cells = set([(y,x) for x in range(l,r) for y in range(t,b)])
	    free_cells.difference_update(used_cells)
	table.foreach(func)
        return free_cells
        
        
    def launch(self, button, command):
	self.running_process = Popen([command])
    
    def get_config(self):
    	#etree = ETree.ElementTree()
    	#config = etree.parse("config/docktable.xml")
    	#return config
        pass
    
    
    def launcher_right_clicked(self, button, event):
	if(event.button != 3): 
            return False 
        menu = gtk.Menu()
        addButton = gtk.MenuItem("Add a Launcher")
        addButton.connect("activate", self._show_add_launcher_gui)
        menu.add(addButton)

        removeButton = gtk.MenuItem("Remove Launcher")
        removeButton.connect("activate", self._remove_launcher, button)
        menu.append(removeButton)
        menu.show_all()
        
        menu.popup(None, None, None, event.button, event.time)
   

    def _show_add_launcher_gui(self, data):
        diag = addlauncherdialog.AddLauncherDialog(self._add_single_launcher)
        diag.show()


    def _remove_launcher(self, data, launcher):
        launcher.destroy()

        
    def launcher_gui_cb(self, data, win, entry):
	result = entry.get_text()
	print result
	win.hide_all()