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

import sys; sys.path += ['lib/', 'config/', 'gizmos']
#from omnilib.specto_wrapper import SpectoWrapper
from omnilib import gui
import appconfig
import gtk
import imp
import sys, os

class omniDOCK():
    """
    Main class that coordinates and controls all logic for omniDock
    """

    def __init__(self):

        self.appConfig = appconfig.DockConfig()
        self.appConfig.load()
        self.appConfig.save()

        #instatiate gui and apply config
        dockGui = gui.OmniDOCKGUI()
        dockGui.apply_config(self.appConfig)
        #The table contains all dock widgets
        self.table = dockGui.table
        dockGui.show_all()
        self.gizmo_import()


    def get_gizmos(self):
	#Currently hardcoded a single gizmo for testing
	#giz = fish.get_gizmo()
	#self.table.add_gizmo(giz)
	pass
   

    def gizmo_import(self):
            gizmoDirs = list(os.walk('./gizmos'))
            gizmoDirs.pop(0)
            for subDir in gizmoDirs:
                fullPath = subDir[0]
                name = fullPath.split('/').pop()
                f, filename, description = imp.find_module(name)
                module = imp.load_module(name, f, filename, description)
                gizmo = module.get_gizmo()
                location = {}
                if len(gizmo) > 3:
                    coords = gizmo[3]
                    print "coords =", coords
                    location["left_attach"] = coords[0]
                    location["right_attach"] = coords[1]
                    location["top_attach"] = coords[2]
                    location["bottom_attach"] = coords[3]
                else:
                    location = self.table.find_space(gizmo)
                self.table.attach(gizmo[0], location["left_attach"],
                                         location["right_attach"],
                                         location["top_attach"],
                                         location["bottom_attach"])

             

if __name__ == "__main__":
    omnidock = omniDOCK()
    gtk.main()
