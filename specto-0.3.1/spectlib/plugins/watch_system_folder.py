# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_system_folder.py
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
import re
from stat import *

type = "Watch_system_folder"
type_desc = _("Folder")
icon = 'folder'
category = _("System")


def get_add_gui_info():
    return [("folder", spectlib.gtkconfig.FolderChooser(_("Folder")))]


class Watch_system_folder(Watch):
    """
    Watch class that will check if a folder has been changed.
    """

    def __init__(self, specto, id, values):
        watch_values = [("folder", spectlib.config.String(True))]

        self.icon = icon
        self.standard_open_command = "xdg-open '%s'" % values['folder']
        self.type_desc = type_desc

        #Init the superclass and set some specto values
        Watch.__init__(self, specto, id, values, watch_values)

        self.cache_file = os.path.join(self.specto.CACHE_DIR, "folder" + self.folder.replace("/", "_") + ".cache")
        self.first_time = False
        self.info = {}
        self.info['removed'] = [0, ""]
        self.info['created'] = [0, ""]
        self.info['modified'] = [0, ""]

    def check(self):
        """ See if a folder's contents were modified or created. """
        try:
            self.old_values = self.read_cache_file()
            mode = os.stat(self.folder)[ST_MODE]
            self.new_files = []
            if S_ISDIR(mode):
                self.get_dir(self.folder)
                self.update_cache_file()#write the new values to the cache file
                self.old_values = self.read_cache_file() #read the new valeus
                self.get_removed_files() #remove the files that were removed
                self.update_cache_file()#write the values (with the removed lines) to the cache file
            else:
                self.set_error(_('The watch is not set to a folder'))

            #first time don't mark as changed
            if self.first_time == True:
                self.actually_changed = False
                self.first_time = False
        except:
            self.set_error()

        Watch.timer_update(self)

    def get_file(self, file_):
        """ Get the info from a file and compair it with the previous info. """
        size = int(os.stat(file_)[6]) #mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime = info
        file_ = file_.replace("?", "\?") \
                     .replace("(", "\(") \
                     .replace(")", "\)") \
                     .replace("^", "\^") \
                     .replace("[", "\[") \
                     .replace("]", "\]") \
                     .replace("$", "\$") \
                     .replace("+", "\+") \
                     .replace(".", "\.")
                     #.replace("\", "\\")
        old_size = re.search('%s:separator:(.+)' % file_, self.old_values)
        file_ = file_.replace("\?", "?") \
                     .replace("\(", "(") \
                     .replace("\)", ")") \
                     .replace("\^", "^") \
                     .replace("\[", "[") \
                     .replace("\]", "]") \
                     .replace("\$", "$") \
                     .replace("\+", "+") \
                     .replace("\.", ".")
                     #.replace("\\", "\")

        if old_size and str(size):
            old_size = int(old_size.group(1))
            if size != old_size:
                #replace filesize
                self.old_values = self.old_values.replace(file_ + ":separator:" + str(old_size), file_ + ":separator:" + str(size))
                self.info['modified'][0] += 1
                self.info['modified'][1] += file_ + "\n"
                self.actually_changed = True
        elif (size or size ==0) and not old_size:
            #add the file to the list
            self.old_values += file_ + ":separator:" + str(size) + "\n"
            self.info['created'][0] += 1
            self.info['created'][1] += file_ + "\n"
            self.actually_changed = True

    def get_dir(self, dir_):
        """ Recursively walk a directory. """
        for f in os.listdir(dir_):
            pathname = os.path.join(dir_, f)
            mode = os.stat(pathname)[ST_MODE]
            if S_ISDIR(mode): # It's a directory, recurse into it
                self.get_dir(pathname)
            elif S_ISREG(mode): # It's a file, get the info
                self.new_files.append(pathname)
                self.get_file(pathname)
            else: # Unknown file type
                self.specto.logger.log(_("Skipping %s") % pathname, "debug", self.name)

    def get_removed_files(self):
        """ Get the removed files. """
        old_values_ = self.old_values.split("\n")
        self.old_values = ""
        y = 0
        for file_ in self.old_files:
            if file_ not in self.new_files:#see if a old file still exists in the new files list
                self.info['removed'][0] += 1
                self.info['removed'][1] += file_ + "\n"
                self.actually_changed = True
            else:
                self.old_values += old_values_[y] + "\n"
            y += 1

    def get_balloon_text(self):
        """ create the text for the balloon """
        created = self.info['created'][0]
        removed = self.info['removed'][0]
        modified = self.info['modified'][0]
        text = ""
        if created > 0:
            if created == 1:
                text += _("1 new file was created.\n")
            else:
                text += str(created) + _(" new files were created.\n")
        if removed > 0:
            if removed == 1:
                text += _("1 file was removed.\n")
            else:
                text += str(removed) + _(" files were removed.\n")
        if modified > 0:
            if modified == 1:
                text += _("1 file was modified.\n")
            else:
                text += str(modified) + _(" files were modified.\n")

        return text

    def get_extra_information(self):
        created = self.info['created'][0]
        removed = self.info['removed'][0]
        modified = self.info['modified'][0]
        text = ""
        if created > 0:
            text += '<span foreground=\"green\">' + self.escape(self.info['created'][1]) + '</span>'
        if removed > 0:
            text += '<span foreground=\"red\">' + self.escape(self.info['removed'][1]) + '</span>'
        if modified > 0:
            text += '<span foreground=\"yellow\">' + self.escape(self.info['modified'][1]) + '</span>'

        return text

    def update_cache_file(self):
        """ Write the new values in the cache file. """
        try:
            f = file(self.cache_file, "w")
            f.write(str(self.old_values))
        except:
            self.specto.logger.log(_("There was an error writing to the file %s") % self.cache_file, "critical", self.name)
        finally:
            f.close()

    def read_cache_file(self):
        """ Read the options from the cache file. """
        try:
            text = ""
            if os.path.exists(self.cache_file):
                f = file(self.cache_file, "r")# Load up the cached version
                self.old_files = []
                for line in f:
                    self.old_files.append(line.split(':separator:')[0])
                    text += line
                f.close()
            else:
                self.first_time = True

            return text
        except:
            self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)

    def remove_cache_files(self):
        os.unlink(self.cache_file)

    def get_gui_info(self):
        return [
                (_('Name'), self.name),
                (_('Last changed'), self.last_changed),
                (_('Folder'), self.folder),
                ]
