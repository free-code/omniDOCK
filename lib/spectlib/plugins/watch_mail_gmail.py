# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_mail_gmail.py
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
from urllib2 import URLError

import spectlib.tools.web_proxy as web_proxy
from spectlib.watch import Watch
import spectlib.config
import spectlib.gtkconfig
from spectlib.i18n import _
import spectlib.util

type = "Watch_mail_gmail"
type_desc = _("GMail")
icon = 'emblem-mail'
category = _("Mail")


def get_add_gui_info():
    return [("username", spectlib.gtkconfig.Entry(_("Username"))),
            ("password", spectlib.gtkconfig.PasswordEntry(_("Password"))),
            ("label", spectlib.gtkconfig.Entry(_("Label"), "Inbox"))]


class Watch_mail_gmail(Watch):
    """
    this watch will check if you have a new mail on your gmail account
    """

    def __init__(self, specto, id, values):
        watch_values = [("username", spectlib.config.String(True)),
                        ("password", spectlib.config.String(True)),
                        ("label", spectlib.config.String(False))]
        url = "https://mail.google.com"
        self.standard_open_command = spectlib.util.return_webpage(url)

        #Init the superclass and set some specto values
        Watch.__init__(self, specto, id, values, watch_values)

        if self.open_command == self.standard_open_command: #check if google apps url has to be used
            if "@" in self.username and not "@gmail.com" and not "@googlemail.com" in self.username:
                url = "http://mail.google.com/a/" + self.username.split("@")[1]  # We use mail.google.com instead of gmail.com because of the trademark issue in Germany
                self.standard_open_command = spectlib.util.return_webpage(url)
                self.open_command = self.standard_open_command

        self.use_network = True
        self.icon = icon
        self.type_desc = type_desc
        self.cache_file = os.path.join(self.specto.CACHE_DIR, "gmail" + self.username + ".cache")

        #watch specific values
        self.oldMsg = 0
        self.newMsg = 0
        self.mail_info = Email_collection()

        self.read_cache_file()

    def check(self):
        """ Check for new mails on your gmail account. """
        try:
            if "@" not in self.username:
                self.username += "@gmail.com"
            s = GmailAtom(self.username, self.password, self.label)
            s.refreshInfo()
            self.oldMsg = s.getUnreadMsgCount()
            self.newMsg = 0
            self.mail_info.clear_old()
            if self.oldMsg == 0:#no unread messages, we need to clear the watch
                self.mark_as_read()
            else:
                i = 0
                while i < self.oldMsg and i < 20: # i < 20 is a hack around the gmail limitation of metadata retrieval (does not affect message count)
                    info = Email(s.getMsgAuthorName(i), s.getMsgTitle(i), s.getMsgSummary(i))
                    if self.mail_info.add(info): #check if it is a new email or just unread
                        self.actually_changed = True
                        self.newMsg += 1
                    i += 1
            self.mail_info.remove_old()
            self.write_cache_file()
        except URLError, e:
            self.set_error(str(e))  # This '%s' string here has nothing to translate
        except:
            self.set_error()
        Watch.timer_update(self)

    def get_gui_info(self):
        return [(_("Name"), self.name),
                (_("Last changed"), self.last_changed),
                (_("Username"), self.username),
                (_("Unread messages"), self.oldMsg)]

    def get_balloon_text(self):
        """ create the text for the balloon """
        unread_messages = self.mail_info.get_unread_messages()
        if len(unread_messages) == 1:
            text = _("New message from <b>%s</b>...\n\n... <b>totalling %d</b> unread mails.") % (unread_messages[0].author, self.oldMsg)
        else:
            i = 0 #show max 4 mails
            author_info = ""
            while i < len(unread_messages) and i < 4:
                author_info += unread_messages[i].author + ", "
                if i == 3 and i < len(unread_messages) - 1:
                    author_info += "and others..."
                i += 1
            author_info = author_info.rstrip(", ")
            text = _("%d new messages from <b>%s</b>...\n\n... <b>totalling %d</b> unread mails.") % (self.newMsg, author_info, self.oldMsg)
        return text

    def get_extra_information(self):
        i = 0
        text = ""
        while i < len(self.mail_info) and i < 4:
            name = self.escape(self.mail_info[i].author)
            subject = self.escape(self.mail_info[i].subject)
            text += "<b>" + name + "</b>: <i>" + subject + "</i>\n"
            if i == 3 and i < len(self.mail_info) - 1:
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
                    info = line.split("&Separator;")
                    email = Email(info[0], info[1], info[2].replace("\n", ""))
                    self.mail_info.add(email)
            finally:
                f.close()

    def write_cache_file(self):
        try:
            f = open(self.cache_file, "w")
        except:
            self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)
        else:
            for email in self.mail_info:
                f.write(email.author + "&Separator;" + email.subject + "&Separator;" + email.summary + "\n")

        finally:
            f.close()

    def remove_cache_files(self):
        os.unlink(self.cache_file)


class Email():

    def __init__(self, author, subject, summary):
        self.id = author + subject + summary
        self.subject = subject
        self.author = author
        self.summary = summary
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


# -*- coding: utf-8 -*-

# gmailatom 0.0.1
#
# HOW TO USE:
# 1) Create an instance of 'GmailAtom' class. The two arguments
#    its constructor take are the username (including '@gmail.com')
#    and the password.
# 2) To retrieve the account status call 'refreshInfo()'.
# 3) To get the unread messages count call 'getUnreadMsgCount()'.
#    You MUST call 'refreshInfo()' at least one time before using
#    this method or it will return zero.
# 4) To get specific information about an unread email you must
#    call the corresponding getter method passing to it the number
#    of the message. The number zero represents the newest one.
#    You MUST call 'refreshInfo()' at least one time before using any
#    getter method or they will return an empty string.
#    The getter methods are:
#    getMsgTitle(index)
#    getMsgSummary(index)
#    getMsgAuthorName(index)
#    getMsgAuthorEmail(index)
#
# by Juan Grande
# juan.grande@gmail.com

from xml.sax.handler import ContentHandler
from xml import sax


class Mail:
    # Auxiliar structure
    title = ""
    summary = ""
    author_name = ""
    author_addr = ""


class MailHandler(ContentHandler):
    """
    Sax XML Handler
    """
    # Tags
    TAG_FEED = "feed"
    TAG_FULLCOUNT = "fullcount"
    TAG_ENTRY = "entry"
    TAG_TITLE = "title"
    TAG_SUMMARY = "summary"
    TAG_AUTHOR = "author"
    TAG_NAME = "name"
    TAG_EMAIL = "email"

    # Path the information
    PATH_FULLCOUNT = [TAG_FEED, TAG_FULLCOUNT]
    PATH_TITLE = [TAG_FEED, TAG_ENTRY, TAG_TITLE]
    PATH_SUMMARY = [TAG_FEED, TAG_ENTRY, TAG_SUMMARY]
    PATH_AUTHOR_NAME = [TAG_FEED, TAG_ENTRY, TAG_AUTHOR, TAG_NAME]
    PATH_AUTHOR_EMAIL = [TAG_FEED, TAG_ENTRY, TAG_AUTHOR, TAG_EMAIL]

    def __init__(self):
        self.startDocument()

    def startDocument(self):
        self.entries = list()
        self.actual = list()
        self.mail_count = "0"

    def startElement(self, name, attrs):
        # update actual path
        self.actual.append(name)

        # add a new email to the list
        if name == "entry":
            m = Mail()
            self.entries.append(m)

    def endElement(self, name):
        # update actual path
        self.actual.pop()

    def characters(self, content):
        # New messages count
        if (self.actual == self.PATH_FULLCOUNT):
            self.mail_count = self.mail_count+content

        # Message title
        if (self.actual == self.PATH_TITLE):
            temp_mail = self.entries.pop()
            temp_mail.title = temp_mail.title+content
            self.entries.append(temp_mail)

        # Message summary
        if (self.actual == self.PATH_SUMMARY):
            temp_mail = self.entries.pop()
            temp_mail.summary = temp_mail.summary+content
            self.entries.append(temp_mail)

        # Message author name
        if (self.actual == self.PATH_AUTHOR_NAME):
            temp_mail = self.entries.pop()
            temp_mail.author_name = temp_mail.author_name+content
            self.entries.append(temp_mail)

        # Message author email
        if (self.actual == self.PATH_AUTHOR_EMAIL):
            temp_mail = self.entries.pop()
            temp_mail.author_addr = temp_mail.author_addr+content
            self.entries.append(temp_mail)

    def getUnreadMsgCount(self):
        return int(self.mail_count)


class GmailAtom:
    """
    The mail class
    """
    realm = "New mail feed"
    host = "https://mail.google.com"
    url = host + "/mail/feed/atom"

    def __init__(self, user, pswd, label):
        if label:
            self.url = self.url + "/" + label
        self.m = MailHandler()
        # initialize authorization handler
        auth_handler = web_proxy.urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(self.realm, self.host, user, pswd)
        opener = web_proxy.urllib2.build_opener(auth_handler)
        web_proxy.urllib2.install_opener(opener)

    def sendRequest(self):
        return web_proxy.urllib2.urlopen(self.url)

    def refreshInfo(self):
        # get the page and parse it
        p = sax.parseString(self.sendRequest().read(), self.m)

    def getUnreadMsgCount(self):
        return self.m.getUnreadMsgCount()

    def getMsgTitle(self, index):
        return self.m.entries[index].title

    def getMsgSummary(self, index):
        return self.m.entries[index].summary

    def getMsgAuthorName(self, index):
        return self.m.entries[index].author_name

    def getMsgAuthorEmail(self, index):
        return self.m.entries[index].author_email
