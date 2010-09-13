# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       networkmanager.py
#
# Copyright (c) 2006-2007 Christopher Halse Rogers

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

import dbus
import dbus.glib
import urllib2
import gobject
import time


def get_net_listener():
    try:
        listener = NMListener(dbus.SystemBus())
        if not listener.has_networkmanager():
            listener = FallbackListener()
    except dbus.DBusException:
        listener = FallbackListener()
    return listener


class CallbackRunner(object):

    def __init__(self):
        self.callbacks = {}

    def add_callback(self, callback, *args, **kwargs):
        self.callbacks[callback] = (args, kwargs)

    def _run_callbacks(self):
        # We can't delete items from a dict we're iterating over
        # so we must make a copy first
        cb = dict(self.callbacks)
        for fn, (args, kwargs) in cb.iteritems():
            fn(*args, **kwargs)
            del self.callbacks[fn]


class NMListener(CallbackRunner):
    statusTable = {0: u'Unknown',
                   1: u'Asleep',
                   2: u'Connecting',
                   3: u'Connected',
                   4: u'Disconnected'}

    def __init__(self, bus):
        super(NMListener, self).__init__()
        self.nm_7 = False
        nmProxy = bus.get_object('org.freedesktop.NetworkManager',
                                 '/org/freedesktop/NetworkManager')

        try:
            self.nmIface = dbus.Interface(nmProxy, "org.freedesktop.DBus.Properties")
            bus.add_signal_receiver(self.on_nm_event,
                                      'StateChanged',
                                      'org.freedesktop.NetworkManager',
                                      'org.freedesktop.NetworkManager',
                                      '/org/freedesktop/NetworkManager')
            self.lastStatus = self.nmIface.Get("org.freedesktop.NetworkManager", "State")
            self.nm_7 = True
        except:
            self.nmIface = dbus.Interface(nmProxy, 'org.freedesktop.NetworkManager')
            self.nmIface.connect_to_signal('DeviceNoLongerActive',
                                           self.on_nm_event,
                                           'org.freedesktop.NetworkManager')
            self.nmIface.connect_to_signal('DeviceNowActive',
                                           self.on_nm_event,
                                           'org.freedesktop.NetworkManager')
            self.lastStatus = self.nmIface.state()

    def on_nm_event(self, *args, **kwargs):
        wasConnected = self.connected()
        if self.nm_7:
            self.lastStatus = self.nmIface.Get("org.freedesktop.NetworkManager", "State")
        else:
            self.lastStatus = self.nmIface.state()
        if (not wasConnected) and self.connected():
            self._run_callbacks()

    def connected(self):
        return self.lastStatus == 3

    def has_networkmanager(self):
        ### It seems that the only way of being sure the service exists
        ### is to actually try to use it!
        try:
            if self.nm_7:
                self.nmIface.Get("org.freedesktop.NetworkManager", "State")
            else:
                self.nmIface.state()
        except dbus.DBusException:
            return False
        return True


class FallbackListener(CallbackRunner):

    def __init__(self):
        self.last_checked = 0
        self._lastConnected = self.connected()
        self._timer_id = gobject.timeout_add(int(10*60*1000), self._callback)

    def connected(self):
        if (time.time() - self.last_checked) > 10*60:
            self.last_checked = time.time()
            try:
                # try to see if google can be reached
                # i.e. connection to internet is up
                ping = urllib2.urlopen('http://www.google.com')
                ping.close()
                self._lastConnected = True
            except IOError:
                self._lastConnected = False

        return self._lastConnected

    def _callback(self):
        wasConnected = self._lastConnected
        self._lastConnected = self.connected()
        if (not wasConnected) and self._lastConnected:
            self._run_callbacks()
