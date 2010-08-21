# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_sn_facebook.py
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
import spectlib.tools.web_proxy as web_proxy
from spectlib.i18n import _

import os
import formatter
import htmllib
import re
from cStringIO import StringIO

type = "Watch_sn_facebook"
type_desc = _("Facebook")
icon = 'facebook'
category = _("Social networks")


def get_add_gui_info():
    return [("email", spectlib.gtkconfig.Entry(_("Email"))),
            ("password", spectlib.gtkconfig.PasswordEntry(_("Password")))]


class Watch_sn_facebook(Watch):
    """
    Watch class that will check for changes in a user's Facebook account.
    """

    def __init__(self, specto, id, values):

        watch_values = [("email", spectlib.config.String(True)),
                        ("password", spectlib.config.String(True))]

        self.icon = icon
        self.type_desc = type_desc

        url = "http://www.facebook.com"
        self.standard_open_command = spectlib.util.return_webpage(url)

        #Init the superclass and set some specto values
        Watch.__init__(self, specto, id, values, watch_values)

        self.cache_file = os.path.join(self.specto.CACHE_DIR, "facebook" + self.email + ".cache")
        self.previous_messages = []
        self.previous_notifications = []
        self.previous_requests = []
        self.previous_wall = []

        self.use_network = True

        self.read_cache_file()

    def check(self):
        """ See if a there are new facebook items. """
        try:
            self.updates = {'message': [], 'notification': [], 'request': [], 'wall': []}
            #message
            facebook = Facebook(self.email, self.password)
            if facebook.connect():
                self.messages = facebook.get_messages()
                for message in self.messages:
                    if message.sender + ": " + message.message not in self.previous_messages:
                        self.updates['message'].append(message.sender + ": " + message.message)
                        self.actually_changed = True
                        self.previous_messages.append(message.sender + ": " + message.message)

                # Facebook notifications
                self.notifications = facebook.get_notifications()
                for notification in self.notifications:
                    if notification.notification not in self.previous_notifications:
                        self.updates['notification'].append(notification.notification)
                        self.actually_changed = True
                        self.previous_notifications.append(notification.notification)

                # Requests
                self.requests = facebook.get_requests()
                for request in self.requests:
                    if request.request not in self.previous_requests:
                        self.updates['request'].append(request.request)
                        self.actually_changed = True
                        self.previous_requests.append(request.request)

                # Wall posts
                self.wall = facebook.get_wall()
                for w in self.wall:
                    if w.poster + ": " + w.post not in self.previous_wall:
                        self.updates['wall'].append(w.poster + ": " + w.post)
                        self.actually_changed = True
                        self.previous_wall.append(w.poster + ": " + w.post)

                self.write_cache_file()
                if len(self.messages) == 0 and len(self.notifications) == 0 and len(self.requests) == 0 and len(self.wall) == 0:
                    self.mark_as_read()
            else:
                self.set_error((_("Wrong username/password")))
        except:
            self.set_error()

        Watch.timer_update(self)

    def get_balloon_text(self):
        """ create the text for the balloon """
        text = _("You received") + " "
        count = len(self.updates['message'])
        if count == 1:
            text += _("a new message") + ", "
        elif count > 1:
            text += _("%d new messages") % (count)
            text += ", "

        count = len(self.updates['notification'])
        if count == 1:
            text += _("a new notification") + ", "
        elif count > 1:
            text += _("%d new notifications") % (count)
            text += ", "

        count = len(self.updates['request'])
        if count == 1:
            text += _("a new request") + ", "
        elif count > 1:
            text += _("%d new requests") % (count)
            text += ", "

        count = len(self.updates['wall'])
        if count == 1:
            text += _("a new wall post") + ", "
        elif count > 1:
            text += _("%d new wall posts") % (count)
            text += ", "

        return text.rstrip(", ")

    def get_extra_information(self):
        i = 0
        info = ""
        for message in self.updates['message']:
            info += message + "\n"
            i += 1

        for notification in self.updates['notification']:
            info += notification + "\n"
            i += 1

        for request in self.updates['request']:
            info += request + "\n"
            i += 1

        for wall in self.updates['wall']:
            info += wall + "\n"
            i += 1

        return self.escape(info)

    def read_cache_file(self):
        if os.path.exists(self.cache_file):
            try:
                f = open(self.cache_file, "r")
            except:
                self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)
            else:
                for line in f:
                    if line.startswith("message:"):
                        self.previous_messages = line.split("message:")[1].split("&Separator;")
                    elif line.startswith("notification:"):
                        self.previous_notifications = line.split("notification:")[1].split("&Separator;")
                    elif line.startswith("request:"):
                        self.previous_requests = line.split("request:")[1].split("&Separator;")
                    elif line.startswith("wall:"):
                        self.previous_wall = line.split("wall:")[1].split("&Separator;")
            finally:
                f.close()

    def write_cache_file(self):
        try:
            f = open(self.cache_file, "w")
        except:
            self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)
        else:
            messages_ = ""
            for message in self.messages:
                messages_ += message.sender + ": " + message.message + "&Separator;"
            f.write("message:" + messages_ + "\n")

            notifications_ = ""
            for notification in self.notifications:
                notifications_ += notification.notification + "&Separator;"
            f.write("notification:" + notifications_ + "\n")

            requests_ = ""
            for request in self.requests:
                requests_ += request.request + "&Separator;"
            f.write("request:" + requests_ + "\n")

            wall_ = ""
            for w in self.wall:
                wall_ += w.poster + ": " + w.post + "&Separator;"
            f.write("wall:" + wall_ + "\n")
        finally:
            f.close()

    def remove_cache_files(self):
        os.unlink(self.cache_file)

    def get_gui_info(self):
        return [(_("Name"), self.name),
                (_("Last changed"), self.last_changed),
                (_("Email"), self.email)]


class Facebook():

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def connect(self):
        opener = web_proxy.urllib2.build_opener(web_proxy.urllib2.HTTPCookieProcessor())
        web_proxy.urllib2.install_opener(opener)
        response = web_proxy.urllib2.urlopen(web_proxy.urllib2.Request("https://login.facebook.com/login.php?m&amp;next=http%3A%2F%2Fm.facebook.com%2Fhome.php", "email=%s&pass=%s&login=Login" % (self.email, self.password)))
        if "form action=\"https://login.facebook.com/login.php" in response.read():
            return False
        else:
            return True

    def get_messages(self):
        connection = web_proxy.urllib2.urlopen("http://m.facebook.com/inbox/")
        messages_ = connection.read().split("<hr />")
        messages = []
        title = ""
        sender = ""
        unread = False
        for line in messages_:
            #search subject
            title = re.search('<a href="/inbox/.+;refid=11">(.+)</a><br /><small><a href="/.+.php', line)
            if title != None:
                outstream = StringIO()
                p = htmllib.HTMLParser(formatter.AbstractFormatter(formatter.DumbWriter(outstream)))
                p.feed(title.group(1))
                title = outstream.getvalue().replace("&#8226;", "")
                outstream.close()

                #search sender
                sender = re.search('</a><br /><small><a href="/.+.php\?.+;refid=11">(.+)</a>(<br />|,)', line)
                if sender != None:
                    sender = sender.group(1)
                else: #multiple receipients
                    sender = re.search('</a><br /><small><a href="/.+.php\?.+;refid=11".+>(.+)</a>(<br />|,)', line)
                    if sender != None:
                        sender = sender.group(1)

            if sender != None and title != None:
                messages.extend([FacebookMessage(sender.strip(), title.strip())])

        return messages

    def get_notifications(self):
        notifications = []
        connection = web_proxy.urllib2.urlopen("http://m.facebook.com/notifications.php")
        messages = connection.read().split("<hr />")
        for line in messages:
            #search notification
            notification = re.search('<div><a href="/.+.php\?.+>(.+)</div>', line)
            if notification != None:
                outstream = StringIO()
                p = htmllib.HTMLParser(formatter.AbstractFormatter(formatter.DumbWriter(outstream)))
                p.feed(notification.group())
                notification = re.sub("(\[.\])", "", outstream.getvalue())
                notification = notification.replace("\n", " ")
                outstream.close()
                notifications.extend([FacebookNotification(notification.strip())])
        return notifications

    def get_requests(self):
        requests = []
        connection = web_proxy.urllib2.urlopen("http://m.facebook.com/reqs.php")
        messages = connection.read().split("<hr />")
        for line in messages:
            #search friend requests
            request = re.search('<a href="/.+.php\?.+refid=.+">(.+)</a></b><br /><table><tr><td colspan="2">', line)
            if request != None:
                outstream = StringIO()
                p = htmllib.HTMLParser(formatter.AbstractFormatter(formatter.DumbWriter(outstream)))
                p.feed(request.group(0))
                request = re.sub("(\[.\])", " ", outstream.getvalue())
                p.close()
                requests.extend([FacebookRequest(request.replace("\n", "").strip())])
        return requests

    def get_wall(self):
        walls = []
        connection = web_proxy.urllib2.urlopen("http://m.facebook.com/wall.php")
        messages = connection.read().split("<hr />")
        for line in messages:
            #search wall poster
            poster = re.search('<a href="/profile.php\?.+refid=.+>(.+)<br /><small>.+</small></div><div>', line)
            if poster != None:
                outstream = StringIO()
                p = htmllib.HTMLParser(formatter.AbstractFormatter(formatter.DumbWriter(outstream)))
                p.feed(poster.group(0))
                poster = re.sub("(\[.+\])", "", outstream.getvalue()).split("\n")[0]
                outstream.close()

            #search wall post
            post = re.search('</small></div><div>(.+)</div>', line)
            if post != None:
                outstream = StringIO()
                p = htmllib.HTMLParser(formatter.AbstractFormatter(formatter.DumbWriter(outstream)))
                p.feed(post.group(0))
                post = re.sub("(\[.+\])", "", outstream.getvalue()).replace("delete", "")
                outstream.close()

            if poster != None and post != None:
                walls.extend([FacebookWall(poster.strip(), post.strip().replace("\n", " "))])
        return walls


class FacebookMessage():

    def __init__(self, sender, message):
        self.sender = sender
        self.message = message


class FacebookNotification():

    def __init__(self, notification):
        self.notification = notification


class FacebookRequest():

    def __init__(self, request):
        self.request = request


class FacebookWall():

    def __init__(self, poster, post):
        self.poster = poster
        self.post = post
