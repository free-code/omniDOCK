# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       watch_web_greader.py
#
# See the AUTHORS file for copyright ownership information

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or(at your option) any later version.
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
import spectlib.util
import spectlib.tools.web_proxy as web_proxy

type = "Watch_web_greader"
type_desc = _("Google Reader")
icon = 'internet-news-reader'
category = _("Internet")


def get_add_gui_info():
    return [("username", spectlib.gtkconfig.Entry(_("Username"))),
           ("password", spectlib.gtkconfig.PasswordEntry(_("Password")))]


class Watch_web_greader(Watch):
    """
    this watch will check if you have new news on your google reader account
    """

    def __init__(self, specto, id, values):
        watch_values = [("username", spectlib.config.String(True)),
                      ("password", spectlib.config.String(True))]

        url = "http://www.google.com/reader/"
        self.standard_open_command = spectlib.util.return_webpage(url)

        #Init the superclass and set some specto values
        Watch.__init__(self, specto, id, values, watch_values)

        self.use_network = True
        self.icon = icon
        self.type_desc = type_desc
        self.cache_file = os.path.join(self.specto.CACHE_DIR, "greader" + self.username + ".cache")

        #watch specific values
        self.unreadMsg = 0
        self.newMsg = 0
        self.news_info = Feed_collection()
        self.or_more = ""

        self.read_cache_file()

    def check(self):
        """ Check for new news on your greader account. """
        try:
            self.newMsg = 0
            greader = Greader(self.username, self.password)
            unread, info_friends, info = greader.refresh()
            if unread[0] == -1:
                self.error = True
                self.specto.logger.log(('%s') % unread[1], "error", self.name)
            elif unread[0] == 1:#no unread items, we need to clear the watch
                self.mark_as_read()
                self.news_info = Feed_collection()
            else:
                self.unreadMsg = int(unread[1])

                if self.unreadMsg == 1000:
                    self.or_more = _(" or more")

                self.news_info.clear_old()

                for feed in info:
                    _feed = Feed(feed, info[feed])
                    if self.news_info.add(_feed):
                        self.actually_changed = True
                        self.newMsg += 1

                self.news_info.remove_old()
                self.write_cache_file()

        except:
            self.set_error()

        Watch.timer_update(self)

    def get_gui_info(self):
        return [(_('Name'), self.name),
               (_('Last changed'), self.last_changed),
               (_('Username'), self.username),
               (_('Unread messages'), str(self.unreadMsg) + self.or_more)]

    def get_balloon_text(self):
        """ create the text for the balloon """
        unread_messages = self.news_info.get_unread_messages()
        if len(unread_messages) == 1:
            text = _("New newsitems in <b>%s</b>...\n\n... <b>totalling %s</b> unread items.") %(unread_messages[0].name, str(self.unreadMsg) + self.or_more)
        else:
            i = 0 #show max 4 feeds
            feed_info = ""
            while i < len(unread_messages) and i < 4:
                feed_info += unread_messages[i].name + ", "
                if i == 3 and i < len(unread_messages) - 1:
                    feed_info += _("and others...")
                i += 1
            feed_info = feed_info.rstrip(", ")
            text = _("%d new newsitems in <b>%s</b>...\n\n... <b>totalling %s</b> unread items.") %(self.newMsg, feed_info, str(self.unreadMsg) + self.or_more)
        return text

    def get_extra_information(self):
        i = 0
        feed_info = ""
        while i < len(self.news_info) and i < 4:
            # TODO: do we need to self.escape the name and messages?
            feed_info += "<b>" + self.news_info[i].name + "</b>: <i>" + str(self.news_info[i].messages) + "</i>\n"
            if i == 3 and i < len(self.news_info) - 1:
                feed_info += _("and others...")
            i += 1
        return feed_info

    def read_cache_file(self):
        if os.path.exists(self.cache_file):
            try:
                f = open(self.cache_file, "r")
            except:
                self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)
            else:
                for line in f:
                    info = line.split("&Separator;")
                    feed = Feed(info[0], info[1].replace("\n", ""))
                    self.news_info.add(feed)

            finally:
                f.close()

    def write_cache_file(self):
        try:
            f = open(self.cache_file, "w")
        except:
            self.specto.logger.log(_("There was an error opening the file %s") % self.cache_file, "critical", self.name)
        else:
            for feed in self.news_info:
                f.write(feed.name + "&Separator;" + str(feed.messages) + "\n")
        finally:
            f.close()

    def remove_cache_files(self):
        os.unlink(self.cache_file)


class Feed():

    def __init__(self, name, messages):
        self.name = name
        self.messages = int(messages)
        self.found = False
        self.new = False


class Feed_collection():

    def __init__(self):
        self.feed_collection = []

    def add(self, feed):
        self.new = True
        self.changed = False
        for _feed in self.feed_collection:
            if feed.name == _feed.name:
                if feed.messages > _feed.messages:
                    self.new = False
                    self.changed = True
                    _feed.messages = feed.messages
                    _feed.found = True
                else:
                    _feed.messages = feed.messages
                    self.new = False
                    _feed.found = True

        if self.new == True:
            feed.found = True
            feed.new = True
            self.feed_collection.append(feed)
            return True
        elif self.changed == True:
            feed.found = True
            feed.updated = True
            return True
        else:
            return False

    def __getitem__(self, id):
        return self.feed_collection[id]

    def __len__(self):
        return len(self.feed_collection)

    def remove_old(self):
        i = 0
        collection_copy = []
        for _feed in self.feed_collection:
            if _feed.found == True:
                collection_copy.append(_feed)
            i += 1
        self.feed_collection = collection_copy

    def clear_old(self):
        for _feed in self.feed_collection:
            _feed.found = False
            _feed.new = False
            _feed.updated = False

    def get_unread_messages(self):
        unread = []
        for _feed in self.feed_collection:
            if _feed.new == True or _feed.updated == True:
                unread.append(_feed)
        return unread


"""
grnotify
---------
GrNotify is a simple Python written tray application that will allow you to know when there are new items in the Google Reader.

GrNotify is written by Kristof Bamps
- And maintained by Bram Bonne and Eric Lembregts


Dependencies
--------------
  * Python >= 2.2 <http://www.python.org>
  * PyXML >= 0.8.3 <http://pyxml.sourceforge.net>
  * PyGTK >= 2.0 <http://www.pygtk.org>
"""
import urllib
import urllib2
import xml.dom.minidom
import os.path

counter = 1 #boolean to show counter or not
numberFeeds = 5 #default maximum number of feeds of which info is shows
L = [] #contains feed ids and their number of unread items
names = [] #contains names of all feeds
feeds = 0 # number of feeds user is subscribed to
email = ''
passwd = ''
cookies = -1
old_unread = -1
unread = 0


def getcookies():
    """
    Use cookies
    """
    COOKIEFILE = os.path.join(spectlib.util.get_path('tmp'), 'cookies.lwp')
    # the path and filename to save your cookies in

    cj = None
    ClientCookie = None
    cookielib = None

    # Let's see if cookielib is available
    try:
        import cookielib
    except ImportError:
        # If importing cookielib fails
        # let's try ClientCookie
        try:
            import ClientCookie
        except ImportError:
        # ClientCookie isn't available either
            urlopen = web_proxy.urllib2.urlopen
            Request = web_proxy.urllib2.Request
        else:
        # imported ClientCookie
            urlopen = ClientCookie.urlopen
            Request = ClientCookie.Request
            cj = ClientCookie.LWPCookieJar()

    else:
        # importing cookielib worked
        urlopen = web_proxy.urllib2.urlopen
        Request = web_proxy.urllib2.Request
        cj = cookielib.LWPCookieJar()
        # This is a subclass of FileCookieJar
        # that has useful load and save methods

    if cj is not None:
    # we successfully imported
    # one of the two cookie handling modules
        # Now we need to get our Cookie Jar
        # installed in the opener;
        # for fetching URLs
        if cookielib is not None:
        # if we use cookielib
        # then we get the HTTPCookieProcessor
        # and install the opener in web_proxy.urllib2
            opener = web_proxy.urllib2.build_opener(web_proxy.urllib2.HTTPCookieProcessor(cj))
            web_proxy.urllib2.install_opener(opener)

        else:
        # if we use ClientCookie
        # then we get the HTTPCookieProcessor
        # and install the opener in ClientCookie
            opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cj))
            ClientCookie.install_opener(opener)

    url = 'https://www.google.com/accounts/ServiceLoginAuth'
    user_agent = 'Mozilla/4.0(compatible; MSIE 5.5; Windows NT)'
    login = {'Email': email, 'Passwd': passwd}

    data = urllib.urlencode(login)

    theurl = url
    # an example url that sets a cookie,
    # try different urls here and see the cookie collection you can make !

    txdata = data
    # if we were making a POST type request,
    # we could encode a dictionary of values here,
    # using urllib.urlencode(somedict)

    txheaders = {'User-agent': 'Mozilla/4.0(compatible; MSIE 5.5; Windows NT)'}
    # fake a user agent, some websites(like google) don't like automated exploration

    try:
        req = Request(theurl, txdata, txheaders)
        # create a request object

        handle = urlopen(req)
        # and open it to return a handle on the url

        del req

    except IOError, e:
        return 2         #we didn't get a connection

    if cj is None:
        return 3         #we got a connection, but didn't get any cookies
    else:
        cj.save(COOKIEFILE)                     # save the cookies again
        return 1, Request, cj        #everything went ok


def getUnreadItems(Request):
    """ Get the number of unread items """
    global unread, L, feeds
    LISTFILE = os.path.join(spectlib.util.get_path('tmp'), 'list.xml')
    url = 'https://www.google.com/reader/api/0/unread-count?all=true'
    try:
        req = Request(url)
        response = web_proxy.urllib2.urlopen(req)
        del req
    except IOError, e:
        return 2         #we didn't get a connection
    testxml = response.read()
    del response
    if '<object>' in testxml:
        fileHandle = open(LISTFILE, 'w')
        fileHandle.write(testxml)
        del testxml
        fileHandle.close()
        fileHandle = open(LISTFILE)
        unread = xml.dom.minidom.parse(fileHandle)
        fileHandle.close()
        del fileHandle
        countlist = unread.getElementsByTagName('number')
        namelist = unread.getElementsByTagName('string')
        for count in countlist:
            if count.attributes["name"].value != 'count':
                countlist.remove(count)
        del unread
        del L[:]
        found = 0
        for i in xrange(0, len(countlist)):
            if 'state/com.google/reading-list' in namelist[i].firstChild.toxml():
                unread = countlist[i].firstChild.toxml()
                found = 1
            else:
                L.append((countlist[i].firstChild.toxml(), namelist[i].firstChild.toxml()))
        del countlist[:]
        del namelist[:]
        if not found: # If there are no subscribed feeds
            unread = '-1'
        L = sorted(L, compare)
        feeds = len(L)
        return 1
    else:
        return 0


def updateFeeds(Request):
    """ Set the names of feeds the user is subscribed to """
    global names, feeds
    LISTFILE = os.path.join(spectlib.util.get_path('tmp'), 'names.xml')
    url = 'http://www.google.com/reader/api/0/subscription/list'
    try:
        req = Request(url)
        response = web_proxy.urllib2.urlopen(req)
        del req
    except IOError, e:
        return 2  # We didn't get a connection
    testxml = response.read()    #read the opened page
    del response
    if '<object>' in testxml:  # If we got a XML file
        fileHandle = open(LISTFILE, 'w')
        fileHandle.write(testxml)
        del testxml
        fileHandle.close
        fileHandle = open(LISTFILE)
        document = xml.dom.minidom.parse(fileHandle)
        fileHandle.close()
        del fileHandle
        del names[:]
        feedlist = document.getElementsByTagName('string')
        for j in xrange(0, len(feedlist)):
            if(feedlist[j].attributes["name"].value == 'id' or feedlist[j].attributes["name"].value == 'title'):
                if('/state/com.google/broadcast' in feedlist[j].firstChild.toxml() or feedlist[j].firstChild.toxml()[0] != 'u'):
                    names.append(feedlist[j].firstChild.toxml())
        del document
        del feedlist[:]


def readFeeds(Request):
    global names
    LISTFILE = os.path.join(spectlib.util.get_path('tmp'), 'names.xml')
    if os.path.isfile(LISTFILE):
        fileHandle = open(LISTFILE)
        document = xml.dom.minidom.parse(fileHandle)
        del names[:]
        feedlist = document.getElementsByTagName('string')
        for j in xrange(0, len(feedlist)):
            if(feedlist[j].attributes["name"].value == 'id' or feedlist[j].attributes["name"].value == 'title'):
                if('/state/com.google/broadcast' in feedlist[j].firstChild.toxml() or feedlist[j].firstChild.toxml()[0] != 'u'):
                    names.append(feedlist[j].firstChild.toxml())
        del document
        del feedlist[:]
        fileHandle.close()
    else:
        updateFeeds(Request)


def compare(a, b):
    """ Compare function to sort the feeds by number of unread items """
    return cmp(int(b[0]), int(a[0]))


class Greader():

    def __init__(self, username, password):
        global unread, info, extra_info, extra_info_friends, email, passwd
        global config_changed
        email = username
        passwd = password
        request = ""

    def refresh(self):
        cookies = getcookies()
        if(cookies[0] == 1):
            request = cookies[1]
            cj = cookies[2]
            cookies = getUnreadItems(request)
        if(cookies == 0):
            info = -1, _('Wrong username or password')
            extra_info = ''
        if(cookies == 2):
            info = -1, _('Could not establish a connection to server')
            extra_info = ''
        if(cookies == 3):
            info = -1, _('Could not get cookies')
            extra_info = ''
        if(cookies != 1):
            cookies = getcookies()

        if(unread == '-1'):
            info = 1, _('You are not subscribed to any feeds')
        elif(unread == '0'):
            info = 1, _('No unread items')
        elif(unread >= '1'):
            info = 2, unread

        readFeeds(request)
        if(len(L) >= numberFeeds):
            i = numberFeeds
        else:
            i = len(L)# - 1
        extra_info = {}
        extra_info_friends = ''
        for i in xrange(0, i):
            found = 0
            for j in xrange(0, len(names)):
                if not found:
                    if(str(L[i][1]) == names[j] or '/state/com.google/broadcast-friends' in L[i][1]) and int(L[i][0]) != 0:
                        found = 1
                        if('/state/com.google/broadcast-friends' in L[i][1]):
                            extra_info_friends += str(L[i][0])
                        else:
                            extra_info.update({names[j+1]: int(L[i][0])})
        del L[:]   #set the table back to empty, so same items don't get added time after time

        try:
            #remove the cache files
            os.unlink(os.path.join(spectlib.util.get_path('tmp'), 'names.xml'))
            os.unlink(os.path.join(spectlib.util.get_path('tmp'), 'cookies.lwp'))
            os.unlink(os.path.join(spectlib.util.get_path('tmp'), 'list.xml'))
        except:
            pass
        cj.clear_session_cookies()
        return info, extra_info_friends, extra_info
