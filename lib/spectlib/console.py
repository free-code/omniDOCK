# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       notifier.py
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
from spectlib.i18n import _


class Console:

    def __init__(self, specto, args):
        self.specto = specto
        self.only_changed = False

        if args:
            if args == "--only-changed":
                self.only_changed = True

    def start_watches(self):
        self.specto.watch_db.restart_all_watches()

    def mark_watch_status(self, status, id):
        """ show the right icon for the status from the watch. """
        watch = self.specto.watch_db[id]

        if status == "changed":
            print watch.name, "-", _("Watch has changed.")
            print watch.get_extra_information()
        elif self.only_changed:
            return
        elif status == "checking":
            print watch.name, "-", _("Watch started checking.")
        elif status == "idle":
            print watch.name, "-", _("Watch is idle.")
        elif status == "no-network":
            print _("No network connection detected")
        elif status == "error":
            print watch.name, "-", _("There was an error checking the watch")
