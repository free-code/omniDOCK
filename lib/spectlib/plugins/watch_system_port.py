# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_system_port.py
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

from spectlib.watch import Watch
import spectlib.config
from spectlib.i18n import _

import os

type = "Watch_system_port"
type_desc = _("Port")
icon = 'network-transmit-receive'
category = _("System")


def get_add_gui_info():
    return [("port", spectlib.gtkconfig.Spinbutton(_("Port"), value=21, upper=65535))]


class Watch_system_port(Watch):
    """
    Watch class that will check if a connection was established on a certain port
    """

    def __init__(self, specto, id, values):
        watch_values = [("port", spectlib.config.Integer(True))]

        self.icon = icon
        self.standard_open_command = ''
        self.type_desc = type_desc
        self.status = ""

        #Init the superclass and set some specto values
        Watch.__init__(self, specto, id, values, watch_values)

        self.running = self.check_port()

    def check(self):
        """ See if a socket was opened or closed. """
        try:
            established = self.check_port()
            if self.running and established == False:
                self.running = False
                self.actually_changed = True
                self.status = _("Closed")
            elif self.running == False and established == True:
                self.running = True
                self.actually_changed = True
                self.status = _("Open")
            else:
                self.actually_changed = False
                self.status = _("Unknown")
        except:
            self.set_error()

        Watch.timer_update(self)

    def check_port(self):
        """ see if there is a connection on the port or not """
        conn = False
        y = os.popen("netstat -nt", "r").read().splitlines()
        del y[0]
        del y[0]
        for k in y:
            k = k.split(' ')
            while True:
                try:
                    k.remove('')
                except:
                    break
            try:
                port = int(k[3][k[3].rfind(':')+1:])
            except:
                port = -1
            if port == int(self.port):
                conn = True

        if conn:
            return True
        else:
            return False

    def get_gui_info(self):
        return [(_('Name'), self.name),
                (_('Last changed'), self.last_changed),
                (_('Port'), self.port),
                (_('Status'), self.status)]

    def get_balloon_text(self):
        """ create the text for the balloon """
        text = ""
        if self.running == True:
            text = _("The network socket on port %s was established.") % self.port
        else:
            text = _("The network socket on port %s was closed.") % self.port
        return text
