# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_vc_bazaar.py
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
import spectlib.gtkconfig
from spectlib.i18n import _
import os

from bzrlib.missing import find_unmerged
from bzrlib.branch import Branch
from bzrlib.errors import NotBranchError

type = "Watch_vc_bazaar"
type_desc = _("Bazaar")
icon = 'bazaar'
category = _("Version control")


def get_add_gui_info():
    return [("folder", spectlib.gtkconfig.FolderChooser(_("Folder")))]


class Watch_vc_bazaar(Watch):
    """
    Watch class that will check if a bzr folder has been changed.
    """

    def __init__(self, specto, id, values):

        watch_values = [("folder", spectlib.config.String(True))]

        self.icon = icon
        self.standard_open_command = "xdg-open '%s'" % values['folder']
        self.type_desc = type_desc

        #Init the superclass and set some specto values
        Watch.__init__(self, specto, id, values, watch_values)

        self.use_network = True

        self.local_branch_ = 0
        self.remote_branch_ = 0
        self.remote_branch_label = ""
        self.local_extra = []
        self.remote_extra = []
        self.cache_file = os.path.join(self.specto.CACHE_DIR, "bazaar" + self.folder.replace("/", "_") + ".cache")

    def check(self):
        """ See if a folder's contents were modified or created. """
        try:
            self.read_cache_file()
            local_branch = Branch.open_containing(self.folder)[0]
            remote_branch = Branch.open_containing(local_branch.get_parent())[0]
            if local_branch.get_parent() != None:
                self.remote_branch_label = local_branch.get_parent().replace("%7E", "~")
                self.local_extra, self.remote_extra = find_unmerged(local_branch, remote_branch)

                if len(self.local_extra) != 0:
                    if int(self.local_extra[len(self.local_extra) - 1][0]) > self.local_branch_:
                        self.actually_changed = True
                        self.write_cache_file()

                if len(self.remote_extra) != 0:
                    if int(self.remote_extra[len(self.remote_extra) - 1][0]) > self.remote_branch_:
                        self.actually_changed = True
                        self.write_cache_file()

                if not self.local_extra and not self.remote_extra:
                    self.mark_as_read()
            else:
                self.set_error(_("No parent branch available, you will not be notified of differences and changes."))

        except NotBranchError, e:
            self.set_error(str(e))
        except:
            self.set_error()

        Watch.timer_update(self)

    def get_balloon_text(self):
        """ create the text for the balloon """
        text = ""
        if len(self.local_extra) != 0:
            if len(self.local_extra) == 1:
                text = _("One new local revision has not yet been merged with its parent branch.")
            else:
                text = _("%d new local revisions have not yet been merged with its parent branch.") % len(self.local_extra)
        if len(self.remote_extra) != 0:
            if len(self.remote_extra) == 1:
                text = _("One new revision on the remote branch.")
            else:
                text = _("%d new revisions on the remote branch.") % len(self.remote_extra)
        return text

    def get_extra_information(self):
        i = 0
        text = ""
        if len(self.remote_extra) != 0:
            while i < len(self.remote_extra) and i < 4:
                text += "<b>Rev " + str(self.remote_extra[i][0]) + "</b>: <i>" + str(self.remote_extra[i][1]).split("@")[0] + "</i>\n"
                if i == 3 and i < len(self.remote_extra) - 1:
                    text += _("and others...")
                i += 1
        if len(self.local_extra) != 0 and text == "":
            while i < len(self.local_extra) and i < 4:
                text += "<b>Rev " + str(self.local_extra[i][0]) + "</b>: <i>" + str(self.local_extra[i][1]).split("@")[0] + "</i>\n"
                if i == 3 and i < len(self.local_extra) - 1:
                    text += _("and others...")
                i += 1
        return text

    def read_cache_file(self):
        if os.path.exists(self.cache_file):
            try:
                f = open(self.cache_file, "r")
            except:
                self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)
            else:
                for line in f:
                    if line.startswith("local_branch:"):
                        self.local_branch_ = int(line.split(":")[1])
                    if line.startswith("remote_branch:"):
                        self.remote_branch_ = int(line.split(":")[1])
            finally:
                f.close()

    def write_cache_file(self):
        try:
            f = open(self.cache_file, "w")
        except:
            self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)
        else:
            if len(self.local_extra) > 0:
                f.write("local_branch:" + str(self.local_extra[len(self.local_extra) - 1][0]) + "\n")
            if len(self.remote_extra) > 0:
                f.write("remote_branch:" + str(self.remote_extra[len(self.remote_extra) - 1][0]) + "\n")
        finally:
            f.close()

    def remove_cache_files(self):
        os.unlink(self.cache_file)

    def get_gui_info(self):
        return [(_('Name'), self.name),
                (_('Last changed'), self.last_changed),
                (_('Folder'), self.folder),
                (_('Main branch'), self.remote_branch_label)]
