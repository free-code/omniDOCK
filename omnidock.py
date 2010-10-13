#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of the omniDOCK project
# See the AUTHORS file for copyright ownership information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

# Name: omnidock.py
# Purpose: Controller for all aspects of omniDOCK

import sys; sys.path += ['lib/', 'config/']
from omnilib.specto_wrapper import SpectoWrapper
from omnilib import gui
import dockconfig
import gtk

class omniDOCK():
    """
    Main class that coordinates and controls all logic for omniDock
    """

    def __init__(self):
	#Load config class (custom elementTree from XML)
	self.appConfig = dockconfig.DockConfig()
    	self.appConfig.load()
    	#Launch specto wrapper
    	#FREDDIE - do you want the callback sent to wrapper's init or
    	#a separate start() function?  
        self.specto = SpectoWrapper()
        #instatiate gui and apply config
        dockGui = gui.OmniDOCKGUI()
        dockGui.apply_config(self.appConfig)
        #The table contains all dock widgets
        self.table = dockGui.table
        dockGui.show_all()
        
        #faking notifications from specto
        self.specto_callback("facebook", 1)
        self.specto_callback("facebook", 2)
        self.specto_callback("facebook", 99)
         
    
    def specto_callback(self, service, value):
	#This function exists to be passed to the specto wrapper
	#It gives the wrapper access to the gui's update_notifier method
	self.table.update_notifier(service, value)
    
    
if __name__ == "__main__":
    omnidock = omniDOCK()
    gtk.main()
