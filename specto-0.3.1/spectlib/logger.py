# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       logger.py
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
import logging
import sys
import os
import re
from datetime import datetime
import traceback
import shutil

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

try:
    import gtk
    import gtk.glade
except:
    pass


class Log_dialog:
    """
    Class to create the log dialog window.
    """

    def __init__(self, specto, notifier):
        self.specto = specto
        self.notifier = notifier
        #create tree
        gladefile = os.path.join(self.specto.PATH, "glade/log_dialog.glade")
        windowname = "log_dialog"
        self.wTree = gtk.glade.XML(gladefile, windowname, \
                                    self.specto.glade_gettext)

        dic = {"on_button_help_clicked": self.show_help,
               "on_button_save_clicked": self.save,
               "on_button_clear_clicked": self.clear,
               "on_button_close_clicked": self.delete_event,
               "on_button_find_clicked": self.find}

        #attach the events
        self.wTree.signal_autoconnect(dic)

        self.log_dialog = self.wTree.get_widget("log_dialog")
        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.log_dialog.set_icon(icon)

        self.wTree.get_widget("combo_level").set_active(0)

        #read the log file
        self.read_log()

        self.logwindow = gtk.TextBuffer(None)
        self.log_buffer = self.wTree.get_widget("log_field").get_buffer()
        self.log_buffer.create_tag("ERROR", foreground="#a40000")
        self.log_buffer.create_tag("INFO", foreground="#4e9a06")
        self.log_buffer.create_tag("WARNING", foreground="#c4a000")
        self.log_buffer.create_tag("DEBUG", foreground="#815902")
        self.log_buffer.create_tag("CRITICAL", foreground="#2e3436")

        start = self.log_buffer.get_start_iter()
        end = self.log_buffer.get_end_iter()
        self.log_buffer.delete(start, end)

        iter = self.log_buffer.get_iter_at_offset(0)
        self.log = self.log.split("\n")
        for line in self.log:
            if line != "":
                tag = line.split(" - ")[1].strip()
                self.log_buffer.insert_with_tags_by_name(iter, \
                                                    line + "\n", tag)

    def save(self, widget):
        """ Save the text in the logwindow. """
        text = self.log_buffer.get_text(self.log_buffer.get_start_iter(), \
                                            self.log_buffer.get_end_iter())
        self.save = Save_dialog(self.specto, text)

    def clear(self, widget):
        """ Clear the text in the log window and from the log file. """
        start = self.log_buffer.get_start_iter()
        end = self.log_buffer.get_end_iter()
        self.log_buffer.delete(start, end)
        f = open(self.file_name, "w")
        f.write("")
        f.close()
        os.chmod(self.file_name, 0600)

    def find(self, widget):
        """ Find the lines in the log file that contain the filter word. """
        self.read_log()
        level = self.wTree.get_widget("combo_level").get_active()
        buffer_log = self.log.split("\n")
        filtered_log = ""

        if level == 1:
            pattern = ("DEBUG")
        elif level == 2:
            pattern = ("INFO")
        elif level == 3:
            pattern = ("WARNING")
        elif level == 4:
            pattern = ("ERROR")
        elif level == 5:
            pattern = ("CRITICAL")
        elif level == -1:
            pattern = self.wTree.get_widget("combo_level").child.get_text()

        start = self.log_buffer.get_start_iter()
        end = self.log_buffer.get_end_iter()
        self.log_buffer.delete(start, end)
        iter = self.log_buffer.get_iter_at_offset(0)

        if level == 0:  # Show everything
            for line in buffer_log:
                if line:  # If the line is not empty
                    tag = line.split(" - ")[1].strip()
                    self.log_buffer.insert_with_tags_by_name(iter, \
                                                        line + "\n", tag)
        else:  # Show the filtered log
            # Do the filtering
            for i in buffer_log:
                if re.search(pattern, i, re.IGNORECASE):
                    filtered_log += i + "\n"
            filtered_log = filtered_log.split("\n")
            for line in filtered_log:
                if line:  # If the line is not empty
                    tag = line.split(" - ")[1].strip()
                    self.log_buffer.insert_with_tags_by_name(iter, \
                                                        line + "\n", tag)

    def read_log(self):
        """ Read the log file. """
        self.file_name = self.specto.SPECTO_DIR + "/specto.log"
        if not os.path.exists(self.file_name):
            f = open(self.file_name, "w")
            f.close()
        os.chmod(self.file_name, 0600)

        log_file = open(self.file_name, "r")
        self.log = log_file.read().replace("&Separator;", " - ")
        log_file.close()

    def show_help(self, widget):
        """ Show the help webpage. """
        self.specto.util.show_webpage(\
         "http://code.google.com/p/specto/wiki/Troubleshooting")

    def delete_event(self, widget, *args):
        """ Close the window. """
        self.log_dialog.destroy()
        return True


class Save_dialog:
    """
    Class for displaying the save as dialog.
    """

    def __init__(self, specto, *args):
        self.specto = specto
        #create tree
        gladefile = os.path.join(self.specto.PATH, "glade/log_dialog.glade")
        windowname = "file_chooser"
        self.wTree = gtk.glade.XML(gladefile, windowname)
        self.save_dialog = self.wTree.get_widget("file_chooser")

        dic = {"on_button_cancel_clicked": self.cancel,
               "on_button_save_clicked": self.save}
        #attach the events
        self.wTree.signal_autoconnect(dic)

        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.save_dialog.set_icon(icon)
        self.save_dialog.set_filename(os.environ['HOME'] + "/ ")

        self.text = args[0]

    def cancel(self, *args):
        """ Close the save as dialog. """
        self.save_dialog.destroy()

    def save(self, *args):
        """ Save the file. """
        file_name = self.save_dialog.get_filename()

        if not os.path.exists(file_name):
            f = open(file_name, "w")
            f.close()
        os.chmod(file_name, 0600)

        f = open(file_name, "w")
        f.write(self.text)
        f.close()

        self.save_dialog.destroy()


class Logger:
    """
    Class for logging in Specto.
    """

    def __init__(self, specto):
        self.specto = specto
        self.file_name = self.specto.SPECTO_DIR + "/specto.log"

        if not os.path.exists(self.file_name):
            f = open(self.file_name, "a")
            f.close()
        os.chmod(self.file_name, 0600)

        self.error_file = self.specto.SPECTO_DIR + "/error.log"
        if not os.path.exists(self.error_file):
            f = open(self.error_file, "a")
            f.close()
        os.chmod(self.error_file, 0600)

        self.log_rotation()

        #write to log file
        #TODO:XXX: Do we need to gettextize it? Maybe just the date.
        logging.basicConfig(level=logging.INFO,
              format='%(asctime)s &Separator; %(levelname)s &Separator;' \
              + ' %(name)s &Separator; %(message)s',
              datefmt='%Y-%m-%d %H:%M:%S',
              filename=self.file_name,
              filemode='a')

        #write to console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        #formatter = logging.Formatter('%(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def log(self, message, level, logger):
        """ Log a message. """
        log = logging.getLogger(str(logger))

        if self.specto.DEBUG == True:
            if level == "debug":
                log.debug(message)
            elif level == "info":
                log.info(message)
            elif level == "warning":
                log.warn(message)
            elif level == "error":
                log.error(message)
                self.log_error()
            else:
                log.critical(message)
                self.log_error()

    def read_log(self):
        """ Read the log file. """
        #get the info from the log file
        log_file = open(self.file_name, "r")
        self.logfile = log_file.read()
        self.logfile.replace("&Separator;", " - ")
        log_file.close()

    def watch_log(self, watch_name):
        """ Filter the log for a watch name. """
        self.read_log()
        buffer_log = self.logfile.split("\n")
        filtered_log = []

        for line in buffer_log:
            if line != "" and line.split("&Separator;")[2].strip() == \
                                                                watch_name:
                info = line.split("&Separator;")
                filtered_log.append([info[1].strip(), info[0] + " - " \
                                                        + info[3] + "\n"])
        return filtered_log

    def remove_watch_log(self, watch_name):
        """ Remove a watch from the log file. """
        self.read_log()
        buffer_log = self.logfile.split("\n")
        filtered_log = ""

        for i in buffer_log:
            if not re.search(watch_name, i) and i != "":
                filtered_log += i + "\n"

        f = open(self.file_name, "w")
        f.write(filtered_log)
        f.close()

    def clear_log(self, *args):
        """ Clear the log file. """
        f = open(self.file_name, "w")
        f.write("")
        f.close()
        os.chmod(self.file_name, 0600)

    def log_error(self):
        error_message = "Error on: " + \
            datetime.today().strftime("%A %d %b %Y %H:%M") + "\n"

        et, ev, tb = sys.exc_info()
        while tb:
            co = tb.tb_frame.f_code
            error_message += "Filename: " + str(co.co_filename) + "\n"
            error_message += "Error Line # : " \
                                + str(traceback.tb_lineno(tb)) + "\n"
            tb = tb.tb_next

        error_message += "Type: " + str(et) + "\n" + "Error: " + \
                                str(ev) + "\n\n"

        f = open(self.error_file, "a")
        f.write(error_message)
        f.close()

    def log_rotation(self):
        if os.path.getsize(self.file_name) > 150000:
            shutil.move(self.file_name, self.file_name + ".1")
            f = open(self.file_name, "a")
            f.close()
            os.chmod(self.file_name, 0600)

        if os.path.getsize(self.error_file) > 150000:
            shutil.move(self.error_file, self.error_file + ".1")
            f = open(self.error_file, "a")
            f.close()
            os.chmod(self.error_file, 0600)
