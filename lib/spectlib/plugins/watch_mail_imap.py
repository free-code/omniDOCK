# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_mail_imap.py
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

import imaplib
import os
from spectlib.i18n import _

type = "Watch_mail_imap"
type_desc = _("IMAP")
icon = 'emblem-mail'
category = _("Mail")


def get_add_gui_info():
    return [("username", spectlib.gtkconfig.Entry(_("Username"))),
            ("password", spectlib.gtkconfig.PasswordEntry(_("Password"))),
            ("host", spectlib.gtkconfig.Entry(_("Host"))),
            ("ssl", spectlib.gtkconfig.CheckButton(_("Use SSL"))),
            ("folder", spectlib.gtkconfig.Entry(_("Folder (optional)")))]


class Watch_mail_imap(Watch):
    """
    Watch class that will check if you recevied a new mail on your pop3 account.
    """

    def __init__(self, specto, id, values):
        watch_values = [("username", spectlib.config.String(True)),
                        ("password", spectlib.config.String(True)),
                        ("host", spectlib.config.String(True)),
                        ("ssl", spectlib.config.Boolean(False)),
                        ("port", spectlib.config.Integer(False)),
                        ("folder", spectlib.config.String(False))]

        self.standard_open_command = spectlib.util.open_gconf_application("/desktop/gnome/url-handlers/mailto")

        Watch.__init__(self, specto, id, values, watch_values)

        self.type_desc = type_desc
        self.use_network = True
        self.icon = icon
        self.cache_file = os.path.join(self.specto.CACHE_DIR, "imap" + self.host + self.username + ".cache")

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
                    server = imaplib.IMAP4_SSL(self.host, self.port)
                else:
                    server = imaplib.IMAP4_SSL(self.host)
            else:
                if self.port != -1:
                    server = imaplib.IMAP4(self.host, self.port)
                else:
                    server = imaplib.IMAP4(self.host)
            server.login(self.username, self.password)
        except imaplib.IMAP4.error, e:
            self.set_error(str(e))
        except:
            self.set_error()
        else:
            try:
                if self.folder != "":
                    try:
                        server.select(self.folder, readonly=1)
                    except:
                        self.set_error()
                else:
                    server.select(readonly=1)
                (retcode, messages) = server.search(None, '(UNSEEN)')
                self.mail_info.clear_old()
                messages = messages[0].split(' ')
                if messages[0] != "":
                    self.unreadMsg = len(messages)
                else:
                    self.unreadMsg = 0
                self.newMsg = 0
                if retcode == 'OK':
                    for message in messages:
                        if message != "":
                            (ret, id) = server.fetch(message, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
                            if ret == 'OK':
                                (ret, subject) = server.fetch(message, '(BODY[HEADER.FIELDS (SUBJECT)])')
                                (ret, sender) = server.fetch(message, '(BODY[HEADER.FIELDS (FROM)])')
                                if ret == 'OK':
                                    id = id[0][1]
                                    id = id.replace("\n", "")
                                    id = id.replace("\r", "")
                                    id = id.lower().replace("message-id: ", "")

                                    subject = subject[0][1]
                                    subject = subject.replace("\n", "")
                                    subject = subject.replace("\r", "")
                                    subject = subject.replace("Subject: ", "")

                                    sender = sender[0][1]
                                    sender = sender.replace("\n", "")
                                    sender = sender.replace("\r", "")
                                    sender = sender.replace("From: ", "")
                                    mail = Email(id, sender, subject)
                                    if self.mail_info.add(mail): #check if it is a new email or just unread
                                        self.actually_changed = True
                                        self.newMsg += 1
                    self.mail_info.remove_old()
                    self.write_cache_file()
                    if len(self.mail_info) == 0:
                        self.mark_as_read()

                server.logout()

            except imaplib.IMAP4.error, e:
                self.set_error(str(e))
            except:
                self.set_error()

        Watch.timer_update(self)
        self.oldMsg = self.newMsg

    def get_balloon_text(self):
        """ create the text for the balloon """
        unread_messages = self.mail_info.get_unread_messages()
        if len(unread_messages) == 1:
            text = _("New message from <b>%s</b>...\n\n... <b>totalling %d</b> unread mails.") % (unread_messages[0].author.split(":")[0], self.unreadMsg)
        else:
            i = 0 #show max 4 mails
            author_info = ""
            while i < len(unread_messages) and i < 4:
                author_info += self.mail_info[i].author + ", "
                if i == 3 and i < len(unread_messages) - 1:
                    author_info += "and others..."
                i += 1
            author_info = author_info.rstrip(", ")
            author_info = author_info.replace("<", "(")
            author_info = author_info.replace(">", ")")
            text = _("%d new messages from <b>%s</b>...\n\n... <b>totalling %d</b> unread mails.") % (self.newMsg, author_info, self.unreadMsg)
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
                    email = Email(info[0], info[1], info[2].replace("\n", ""))
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
                f.write(email.id + "&Separator;" + email.author + "&Separator;" + email.subject + "\n")

        finally:
            f.close()

    def remove_cache_files(self):
        os.unlink(self.cache_file)


class Email():

    def __init__(self, id, author, subject):
        self.id = id
        self.subject = subject
        self.author = author
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

    def get_unread_messages(self):
        unread = []
        for _email in self.email_collection:
            if _email.new == True:
                unread.append(_email)
        return unread
