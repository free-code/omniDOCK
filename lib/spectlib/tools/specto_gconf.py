# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       specto_gconf.py
#
# See the AUTHORS file for copyright ownership information

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

import gconf


class Specto_gconf:
    """
    Specto gconf class.
    """

    def __init__(self, directory):
        # Get the GConf object
        self.client = gconf.client_get_default()
        self.client.add_dir(directory, gconf.CLIENT_PRELOAD_NONE)
        self.directory = directory
        self.org_directory = directory

    def set_directory(self, dir):
        if dir != "": #change the dir
            #check if the dir has to change
            if self.org_directory + dir != self.directory:
                self.directory = self.org_directory + dir
                self.client = gconf.client_get_default()
                self.client.add_dir(self.directory, gconf.CLIENT_PRELOAD_NONE)
        else: #change dir to original dir
            self.directory = self.org_directory
            self.client = gconf.client_get_default()
            self.client.add_dir(self.directory, gconf.CLIENT_PRELOAD_NONE)

    def get_entry(self, key):
        if "/" in key:
            dir = "/" + key[:key.index('/')]
            self.set_directory(dir)
            key = key[key.index('/')+1:]

        k = self.directory + "/" + key

        value = self.client.get(k)

        if value == None:
            return None
        if value.type == gconf.VALUE_STRING:
            return value.get_string()
        elif value.type == gconf.VALUE_BOOL:
            return value.get_bool()
        elif value.type == gconf.VALUE_INT:
            return value.get_int()

    def set_entry(self, key, entry):
        """ Set the value from a key. """
        if "/" in key:
            dir = "/" + key[:key.index('/')]
            self.set_directory(dir)
            key = key[key.index('/')+1:]

        k = self.directory + "/" + key

        if type(entry) == type(str()):
            self.client.set_string(k, entry)
        elif type(entry) == type(bool()):
            self.client.set_bool(k, entry)
        elif type(entry) == type(int()):
            self.client.set_int(k, entry)
        elif type(entry) == type(float()):
            self.client.set_float(k, entry)

    def unset_entry(self, key):
        """ Unset (remove) the key. """
        if "/" in key:
            dir = "/" + key[:key.index('/')]
            self.set_directory(dir)
            key = key[key.index('/')+1:]
        k = self.directory + "/" + key

        self.client.unset(k)

    def notify_entry(self, key, callback, label):
        """ Listen for changes in a key. """
        if "/" in key:
            dir = "/" + key[:key.index('/')]
            self.set_directory(dir)
            key = key[key.index('/')+1:]

        k = self.directory + "/" + key

        self.client.notify_add(k, callback, label)
