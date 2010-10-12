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

class omniDOCK():
    """
    Main class that coordinates and controls all logic for omniDock
    """

    def __init__(self):
	print "For now, click on the window and do alt+f4 to exit"
    	self.appConfig = dockconfig.DockConfig()
    	self.appConfig.load()
    	self.appConfig.save()
        self.specto = SpectoWrapper()
        dockGui = gui.OmniDOCKGUI()
        dockGui.apply_config(self.appConfig)
        dockGui.show_window()
	
    
if __name__ == "__main__":
    omnidock = omniDOCK()
    
