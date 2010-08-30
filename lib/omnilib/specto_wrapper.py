# This file is part of the uberdock project
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

# Name: specto_wrapper.py
# Purpose: Instantiate and use classes from specto


global GTK
global DEBUG #the DEBUG constant which controls how much info is output
GTK = False

import os
import sys
import gobject
import gettext

import spectlib.util as util
from spectlib.watch import Watch_collection
from spectlib.watch import Watch_io
from spectlib.console import Console
from spectlib.logger import Logger
from spectlib.tools.specto_gconf import Specto_gconf
from spectlib.i18n import _
from spectlib.tools import networkmanager as conmgr
from spectlib.notifier import Notifier


class SpectoWrapper(Specto):
    """Reuse code from the specto project"""

    def __init__(self):
#        self.DEBUG = DEBUG
        self.util = util
        self.PATH = self.util.get_path()
        self.SRC_PATH = self.util.get_path("src")
        self.SPECTO_DIR = self.util.get_path("specto")
        self.CACHE_DIR = self.util.get_path("tmp")
        self.FILE = self.util.get_file()
        self.glade_gettext = gettext.textdomain("specto")
#        self.logger = Logger(self)
#        self.check_instance() #see if specto is already running
#        self.specto_gconf = specto_gconf
#        self.check_default_settings()
#        self.GTK = GTK
#        self.connection_manager = conmgr.get_net_listener()
#        self.use_keyring = self.specto_gconf.get_entry("use_keyring")
        
        #create the watch collection and add the watches
        self.watch_db = Watch_collection(self)
        self.watch_io = Watch_io(self, self.FILE)
        
        self.console = Console(self, args)
        
        try:
            self.watch_db.create(values)
        except AttributeError, error_fields:
            self.logger.log(_("Could not create a watch, because it is corrupt."), \
                                "critical", "specto")
        
        self.console.start_watches()

        try:
                self.go = gobject.MainLoop()
                self.go.run()
            except (KeyboardInterrupt, SystemExit):
                sys.exit(0)
                
        
