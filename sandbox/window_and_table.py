# -*- coding: utf-8 -*-
import gtk

#Subclassing standard Window
class MainWindow(gtk.Window): 
  def __init__(self):
    #Running gtk.Window's init method
    super(MainWindow, self).__init__() 
    
    self.set_size_request(400,400)
    #connect gui close button to quit signal
    self.connect("destroy", gtk.main_quit)
    
    self.table = gtk.Table(8,8,True)
    
    
    #--------------------------------------------------
    # This is all junk code for teasting the XML
    #
    launchers = self.get_launchers()
    for i, launcher in enumerate(launchers):
      self.table.attach(launcher, i,i+1,1,2)
    
    self.add(self.table)
    self.show_all()


  def get_launchers(self):
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
  
