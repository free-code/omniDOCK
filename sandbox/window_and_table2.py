# -*- coding: utf-8 -*-
import gtk
from xml.etree.ElementTree import ElementTree

#Subclassing standard Window
class MainWindow(gtk.Window): 
  def __init__(self):
    #Running gtk.Window's init method
    super(MainWindow, self).__init__() 
    
    self.set_size_request(280,700)
    #connect gui close button to quit signal
    self.connect("destroy", gtk.main_quit)
    
    #The table is the real gui, the window just holds it.  
    #Gizmos are added to the table, not the window.  
    self.table = gtk.Table(12,4,True)
    
    #----------------------------------
    etree = ElementTree()
    etree.parse("launchers.xml")
    #XML insists on nesting everything a dozen times
    launchers = etree.find("launchers")
    for i, launcherConfig in enumerate(launchers.getchildren()):
      launcher = gtk.Button()
      launcher.set_label(launcherConfig.find("name").text)
      self.table.attach(launcher, 0, 1, i, i+1)
    #-----------------------------------
      
    #add the table to the window
    self.add(self.table)
    #if you don't show or show_all, no gui
    self.show_all()


  def get_launchers(self):
    """The "builder" object is the bridge between XML and GTK
    we create a builder from XML, use it to get a list of objects (buttons)
    and pass the buttons back in a list"""
    builder = gtk.Builder()
    if builder.add_from_file("button.xml"):
      print "build apparently successful"
    else:
      print "build apparently failed"
    launchers = [x for x in builder.get_objects()]
    return launchers

if __name__ == "__main__":
  MainWindow()
  gtk.main()
  
