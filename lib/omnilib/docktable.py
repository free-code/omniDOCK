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
        newButton = Launcher()
        newButton.lname = details["name"]
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
            
            thisNode = ETree.SubElement(launcherElement, elem)
            thisNode.text = str(details[elem])
        ETree.dump(rootElement)
        rootElement.append(launcherElement)
        self.configTree.save()

	 
    def find_space(self,giz):
	#Faking the intelligent placement for testing
	gizmo = giz[0]
	height = giz[1][0]
	width = giz[1][1]
        freeCells = self.get_free_cells()
        cellno = 0
        row = 0
        holderList = []
        #goodRows is the result of this loop, and holds lists of tuples.  Each
        #list is a row, each tuple is the coordinates of the open cell
        #ie goodRows[0] could be [(2,0), (2,1), (2,2)]
        goodRows = []
        for cell in freeCells:
            if cell[0] != row:
                holderList = []
            for widthi in range(width):
                if (cellno, widthi) in freeCells:
                    holderList.append((cellno, widthi))
                    if len(holderList) >= width:
                        #print "FOUND GOOD WIDTH AT ", holderList
                        goodRows.append(holderList)
            cellno += 1


        #Find good vertical space.  Currently only handles 
        #blank rows
        rownum = 0
        for row in goodRows:
            rownum += 1
            rows = []
            #print "Current good row:", row
            for i in range(height):
                try:
                    rows.append(goodRows[rownum + i][0][0])
                except IndexError:
                    #As the whole idea is to parse ahead for open rows,
                    # it's perfectly ok to get an index error for rows
                    #that don't exist
                    pass
            print "rows", rows
            result = {}
            result["left_attach"] = row[0][1]
            result["right_attach"] = row[0][1] + width
            result["top_attach"] = row[0][0]
            result["bottom_attach"] = row[0][0] + height
            return result
        print >> sys.stderr, "Unable to find space!"


	                
	                
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
        
        menu.popup(None, None, None, eve.button, event.time)
   

    def _show_add_launcher_gui(self, data):
        diag = addlauncherdialog.AddLauncherDialog(self._add_single_launcher)
        diag.show()


    def _remove_launcher(self, data, launcher):
        print launcher.lname
        allLaunchers = self.configTree.findall("launcher")
        for item in allLaunchers:
            if item.findtext("name") == launcher.lname:
                print "found lname"
                self.configTree.getroot().remove(item)
                self.configTree.save()
            print item
            

        launcher.destroy()



class Launcher(gtk.Button):
    def __init__(self):
      super(Launcher, self).__init__()
      self.lname = None