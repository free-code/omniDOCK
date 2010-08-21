# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_mail_pop3.py
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
import spectlib.util

import poplib
import email
import os
from socket import error
from spectlib.i18n import _
import string

type = "Watch_mail_pop3"
type_desc = _("POP3")
icon = 'emblem-mail'
category = _("Mail")


def get_add_gui_info():
    return [("username", spectlib.gtkconfig.Entry(_("Username"))),
            ("password", spectlib.gtkconfig.PasswordEntry(_("Password"))),
            ("host", spectlib.gtkconfig.Entry(_("Host"))),
            ("ssl", spectlib.gtkconfig.CheckButton(_("Use SSL")))]


class Watch_mail_pop3(Watch):
    """
    Watch class that will check if you recevied a new mail on your pop3 account.
    """

    def __init__(self, specto, id, values):

        watch_values = [("username", spectlib.config.String(True)),
                        ("password", spectlib.config.String(True)),
                        ("host", spectlib.config.String(True)),
                        ("ssl", spectlib.config.Boolean(False)),
                        ("port", spectlib.config.Integer(False))]

        self.standard_open_command = spectlib.util.open_gconf_application("/desktop/gnome/url-handlers/mailto")

        Watch.__init__(self, specto, id, values, watch_values)

        self.type_desc = type_desc
        self.use_network = True
        self.icon =icon
        self.cache_file = os.path.join(self.specto.CACHE_DIR, "pop3" + self.host + self.username + ".cache")

        self.newMsg = 0
        self.unreadMsg = 0
        self.mail_id = []
        self.mail_info = Email_collection()

        self.read_cache_file()

    def check(self):
        """ Check for new mails on your pop3 account. """
        try:
            if self.ssl == True:
                if self.port != -1:
                    try:
                        s = poplib.POP3_SSL(self.host, self.port)
                    except:
                        self.set_error()
                        Watch.timer_update(self)
                        return ""
                else:
                    try:
                        s = poplib.POP3_SSL(self.host)
                    except:
                        self.set_error()
                        Watch.timer_update(self)
                        return ""
            else:
                if self.port != -1:
                    try:
                        s = poplib.POP3(self.host, self.port)
                    except:
                        self.set_error()
                        Watch.timer_update(self)
                        return ""
                else:
                    try:
                        s = poplib.POP3(self.host)
                    except:
                        self.set_error()
                        Watch.timer_update(self)
                        return ""
        except poplib.error_protoerror, e:
            self.set_error(str(e))
        except:
            self.set_error()
        else:
            try:
                s.user(self.username)
                s.pass_(self.password)
                self.unreadMsg = len(s.list()[1])
                self.newMsg = 0
                self.mail_info.clear_old()

                if self.unreadMsg > 0:
                    i = 1
                    while i < self.unreadMsg + 1:
                        str_msg = string.join(s.top(i, 0)[1], "\n")
                        msg = email.message_from_string(str_msg)
                        id = string.split(s.uidl(i))[2] #get unique info
                        mail = Email(id, msg["From"].replace("\n", ""), msg["Subject"].replace("\n", ""), msg["date"])
                        if self.mail_info.add(mail): #check if it is a new email or just unread
                            self.actually_changed = True
                            self.newMsg += 1
                        i += 1
                    self.mail_info.sort()
                self.mail_info.remove_old()
                if len(self.mail_info) == 0:
                    self.mark_as_read()
                self.write_cache_file()

                s.quit()

            except poplib.error_proto, e:
                self.set_error(str(e))
            except:
                self.set_error()

        self.oldMsg = self.newMsg
        Watch.timer_update(self)

    def get_balloon_text(self):
        """ create the text for the balloon """
        unread_messages = self.mail_info.get_unread_messages()
        if len(unread_messages) == 1:
            author_info = unread_messages[0].author.split(":")[0]
            author_info = author_info.replace("<", "(")
            author_info = author_info.replace(">", ")")
            text = _("New message from <b>%s</b>...\n\n... <b>totalling %d</b> unread mails.") % (author_info, self.unreadMsg)
        else:
            i = 0 #show max 4 mails
            author_info = ""
            while i < len(unread_messages) and i < 4:
                author_info += self.mail_info[i].author + ", "
                if i == 3 and i < len(unread_messages) - 1:
                    author_info += _("and others...")
                i += 1
            author_info = author_info.rstrip(", ")
            author_info = author_info.replace("<", "(")
            author_info = author_info.replace(">", ")")
            text = _("%d new messages from <b>%s</b>...\n\n... <b>totalling %d</b> unread mails.") % (self.name, self.newMsg, author_info, self.unreadMsg)
        return text

    def get_extra_information(self):
        i = 0
        text = ""
        while i < len(self.mail_info) and i < 4:
            name = self.escape(self.mail_info[i].author.split("<")[0])
            subject = self.escape(self.mail_info[i].subject)
            text += "<b>" + name + "</b>: <i>" + subject + "</i>\n"
            if i == 3 and i < len(self.mail_info) - 1:
                text += _("and others...")
            i += 1
        return text

    def get_gui_info(self):
        return [(_('Name'), self.name),
                (_('Last changed'), self.last_changed),
                (_('Username'), self.username),
                (_('Unread messages'), self.unreadMsg)]

    def read_cache_file(self):
        if os.path.exists(self.cache_file):
            try:
                f = open(self.cache_file, "r")
            except:
                self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)
            else:
                for line in f:
                    info = line.split("&Separator;")
                    email = Email(info[0], info[1], info[2], info[3].replace("\n", ""))
                    self.mail_info.add(email)
            finally:
                f.close()

    def write_cache_file(self):
        try:
            f = open(self.cache_file, "w")
        except:
            self.specto.logger.log(_("There was an error writing to the file %s") % self.cache_file, "critical", self.name)
        else:
            for email in self.mail_info:
                f.write(email.id + "&Separator;" + email.author + "&Separator;" + email.subject + "&Separator;" + email.date + "\n")
        finally:
            f.close()

    def remove_cache_files(self):
        os.unlink(self.cache_file)


class Email():

    def __init__(self, id, author, subject, date):
        self.id = id
        self.subject = subject
        self.author = author
        #FIXME: change date to "year month day time"
        #date = date.split(" ")
        #month = time.strptime(date[1], "%b")
        #self.date = date[2] + " " + str(month[1]) + " " + date[0] + " " + date[3]
        self.date = date
        self.found = False
        self.new = False


class Email_collection():

    def __init__(self):
        self.email_collection = []

    def add(self, email):
        self.new = True
        for _email in self.email_collection:
            if email.id == _email.id:
                self.new = False
                _email.found = True

        if self.new == True:
            email.found = True
            email.new = True
            self.email_collection.append(email)
            return True
        else:
            return False

    def __getitem__(self, id):
        return self.email_collection[id]

    def __len__(self):
        return len(self.email_collection)

    def remove_old(self):
        i = 0
        collection_copy = []
        for _email in self.email_collection:
            if _email.found == True:
                collection_copy.append(_email)
            i += 1
        self.email_collection = collection_copy

    def clear_old(self):
        for _email in self.email_collection:
            _email.found = False
            _email.new = False

    def sort(self):
        self.email_collection.sort(self.sort_function)

    def sort_function(self, x, y):
        if x.date > y.date:
            return 1
        elif x.date == y.date:
            return 0
        else:
            return -1

    def get_unread_messages(self):
        unread = []
        for _email in self.email_collection:
            if _email.new == True:
                unread.append(_email)
        return unread
