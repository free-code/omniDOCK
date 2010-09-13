# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       web_proxy.py
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
import urllib2
#to add a timeout to the global process
import socket
from spectlib.tools.specto_gconf import Specto_gconf

proxy_gconf = Specto_gconf("/system/http_proxy")
socket.setdefaulttimeout(10)# set globally the timeout to 10

if proxy_gconf.get_entry("use_http_proxy"):
    http_proxy = "http://%s:%s" % (proxy_gconf.get_entry("host"), \
                     proxy_gconf.get_entry("port"))

    proxy_gconf = Specto_gconf("/system/proxy")
    https_proxy = "https://%s:%s" % (proxy_gconf.get_entry("secure_host"), \
                    proxy_gconf.get_entry("secure_port"))
    proxy = {"http": http_proxy, "https": https_proxy}

    proxy_support = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(proxy_support)
