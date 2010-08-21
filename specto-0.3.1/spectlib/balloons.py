# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       balloons.py
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

import pygtk
pygtk.require('2.0')
import pynotify
import sys
import gtk
import spectlib.util
from time import sleep
from spectlib.i18n import _

notifyInitialized = False


class NotificationToast:
    _notifyRealm = 'Specto'
    _Urgencies = {'low': pynotify.URGENCY_LOW,
                'critical': pynotify.URGENCY_CRITICAL,
                'normal': pynotify.URGENCY_NORMAL}

    def __open_watch(self, n, action, id):
        if self.specto.notifier.open_watch(id):
            self.specto.notifier.mark_watch_as_read('', id)

    def __init__(self, specto, notifier):
        global notifyInitialized
        self.specto = specto
        self.notifier = notifier

        if not notifyInitialized:
            pynotify.init(self._notifyRealm)
            notifyInitialized = True

        # Check the features available from the notification daemon
        self.capabilities = {'actions': False,
                        'body': False,
                        'body-hyperlinks': False,
                        'body-images': False,
                        'body-markup': False,
                        'icon-multi': False,
                        'icon-static': False,
                        'sound': False,
                        'image/svg+xml': False,
                        'append': False}
        caps = pynotify.get_server_caps()
        if caps is None:
            print "Failed to receive server caps."
            sys.exit(1)
        for cap in caps:
            self.capabilities[cap] = True

    def show_toast(self, body, icon=None, urgency="low", summary=_notifyRealm, name=None):
        tray_x = 0
        tray_y = 0

        if notifyInitialized:
            sleep(0.5)  # FIXME: issue #43, associate the balloon with the notification icon properly. Currently, this is a hack to leave time for the tray icon to appear before getting its coordinates
            tray_x = self.notifier.tray.get_x()
            tray_y = self.notifier.tray.get_y()
            self.toast = pynotify.Notification(summary, body)
            if name:
                # If name is not None and exists in specto.watch_db, a button is added to the notification
                w = self.specto.watch_db.find_watch(name)
                if w != -1 and self.capabilities["actions"]:  # Don't request action buttons if the notification daemon (ex: notify-osd) rejects them
                    self.toast.add_action("clicked", gtk.stock_lookup(gtk.STOCK_JUMP_TO)[1].replace('_', ''), self.__open_watch, w)
            self.toast.set_urgency(self._Urgencies[urgency])
            if icon:
                #self.toast.set_property('icon-name', icon)  # We now use a pixbuf in the line below to allow themable icons
                self.toast.set_icon_from_pixbuf(icon)

            if tray_x != 0 and tray_y != 0:  # grab the x and y position of the tray icon and make the balloon emerge from it
                self.toast.set_hint("x", tray_x)
                self.toast.set_hint("y", tray_y)

            try:
                self.toast.show()
            except:
                self.specto.logger.log(_("Cannot display notification message. Make sure that libnotify and D-Bus are available on your system."), "error", self.specto)
