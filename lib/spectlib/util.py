# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       util.py
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

import os
import sys
from spectlib.tools.specto_gconf import Specto_gconf


def return_webpage(webpage):
    """ Open the webpage in the default browser. """
    specto_gconf = Specto_gconf("/desktop/gnome/url-handlers/http")
    default_browser = specto_gconf.get_entry("command")
    return (default_browser % webpage) #return the browser with the page


def show_webpage(webpage):
    os.system(return_webpage(webpage) + " &")


def open_gconf_application(key):
    """ Get the name from gconf and open the application. """
    specto_gconf = Specto_gconf(key)
    application = specto_gconf.get_entry("command")
    if "mailto" in key:
        application = application.replace(" %s", "")#this is an ugly hack, because evolution really doesn't want to startup with %s
    return application


def get_path(category=None):
    """ Return the correct path. """
    if not os.path.exists('data') or not os.path.exists('spectlib'):
        if not category:
            PATH = "%s/share/specto/" % sys.prefix
        elif category=="doc":
            PATH = "%s/share/doc/specto/" % sys.prefix
        elif category=="src":
            PATH = os.path.dirname(os.path.abspath(__file__))
    else:
        if not category:
            PATH =os.path.join(os.getcwd(), "data/")
        elif category=="doc":
            PATH = os.path.join(os.getcwd(), "data/doc/")
        elif category=="src":
            PATH = os.path.dirname(os.path.abspath(__file__))

    if category == "specto":
        try:
            PATH = os.path.join(os.environ['XDG_CONFIG_HOME'],
                                              "specto")
        except KeyError:
            PATH = os.path.join(os.environ['HOME'], ".config",
                                              "specto")
        if not os.path.exists(PATH):
            os.makedirs(PATH)
            os.chmod(PATH, 0700)  # Meet XDG spec

    if category == "tmp":
        try:
            PATH = os.path.join(os.environ['XDG_CACHE_HOME'],
                                              "specto")
        except KeyError:
            PATH = os.path.join(os.environ['HOME'], ".cache",
                                              "specto")
        if not os.path.exists(PATH):
            os.makedirs(PATH)
            os.chmod(PATH, 0700)  # Meet XDG spec
    return PATH


def get_file():
    try:
        file_name = os.path.join(os.environ['XDG_CONFIG_HOME'],
                                          "specto", "watches.list")
    except KeyError:
        file_name = os.path.join(os.environ['HOME'], ".config",
                                          "specto", "watches.list")
    # Only if file doesn't exist do we need to "open" (create) it.
    if not os.path.exists(file_name):
        dirname = os.path.dirname(file_name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            os.chmod(dirname, 0700)  # Meet XDG spec
        f = open(file_name, "w")
        f.close()
        # As we store passwords make sure only user can read the watch file
        os.chmod(file_name, 0600)
    return file_name
