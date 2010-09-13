# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_system_file.py
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

type = "Watch_system_file"
type_desc = _("File")
icon = 'gnome-mime-text'
category = _("System")


def get_add_gui_info():
    return [("file", spectlib.gtkconfig.FileChooser(_("File")))]


class Watch_system_file(Watch):
    """
    Watch class that will check if a file has been changed.
    """

    def __init__(self, specto, id, values):
        watch_values = [("file", spectlib.config.String(True))]

        self.icon = icon
        self.open_command = ''
        self.type_desc = type_desc
        self.standard_open_command = "xdg-open '%s'" % values['file']

        #Init the superclass and set some specto values
        Watch.__init__(self, specto, id, values, watch_values)

        self.cache_file = os.path.join(self.specto.CACHE_DIR, "file" + self.file.replace("/", "_") + ".cache")
        self.first_time = False

    def check(self):
        """ See if a file was modified or created. """
        try:
            self.info = []
            self.file_info = []
            self.old_info = ""
            self.read_cache_file()
            try:
                info = tuple(os.stat(self.file)) #mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime = info
            except OSError:
                self.actually_changed = True
                self.file_info.append(_("The file was removed"))
            else:
                self.old_info = self.old_info.replace("L", "").replace("[", "").replace("]", "").replace("'", "").split(",")

                i = 0
                while i < len(info):
                    self.info.append(str(info[i]).strip())
                    if not self.first_time:
                        self.old_info[i] = str(self.old_info[i]).strip()
                    i += 1

                if self.old_info != self.info and not self.first_time:
                    self.actually_changed = True

                    #if str(self.info[0]) != self.old_info[0].strip():
                    #    self.file_info.append("Inode protection mode changed")

                    #if str(self.info[1]) != self.old_info[1].strip():
                    #    self.file_info.append("Inode number changed")

                    #if str(self.info[2]) != self.old_info[2]:
                    #    self.file_info.append("Device inode resides on changed")

                    #if self.info[3] != self.old_info[3]:
                    #    self.file_info.append("Number of links to the inode changed")

                    if self.info[4] != self.old_info[4]:
                        self.file_info.append(_("User id of the owner changed"))

                    if self.info[5] != self.old_info[5]:
                        self.file_info.append(_("Group id of the owner changed"))

                    if self.info[6] != self.old_info[6]:
                        self.file_info.append(_("File size changed"))

                    if self.info[7] != self.old_info[7]:
                        self.file_info.append(_("Time of last access changed"))

                    if self.info[8] != self.old_info[8]:
                        self.file_info.append(_("Time of last modification changed"))

                    #if self.info[9] != self.old_info[9]:
                    #    self.file_info.append("Metadata changed")

                self.update_cache_file()
                self.first_time = False
        except:
            self.set_error()

        Watch.timer_update(self)

    def update_cache_file(self):
        """ Write the new values in the cache file. """
        try:
            f = file(self.cache_file, "w")
            f.write(str(self.info))
        except:
            self.specto.logger.log(_("There was an error writing to the file %s") % self.cache_file, "critical", self.name)
        finally:
            f.close()

    def read_cache_file(self):
        """ Read the options from the cache file. """
        try:
            if os.path.exists(self.cache_file):
                f = file(self.cache_file, "r")# Load up the cached version
                self.old_info = f.readline()
                f.close()
            else:
                self.first_time = True

        except:
            self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)

    def remove_cache_files(self):
        os.unlink(self.cache_file)

    def get_balloon_text(self):
        """ create the text for the balloon """
        text = ""
        for line in self.file_info:
            text += line + "\n"

        return text

    def get_extra_information(self):
        text = _("<b>%s</b> has changed:\n") % self.file
        for line in self.file_info:
            text += line + "\n"

        return text

    def get_gui_info(self):
        return [
                (_('Name'), self.name),
                (_('Last changed'), self.last_changed),
                (_('File'), self.file),
                ]
