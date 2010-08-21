# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       gtkutil.py
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
import gtk
import os
from spectlib.i18n import _
import spectlib.util


class Entry():

    def __init__(self, label, text=None):
        self.table = gtk.Table(rows=1, columns=2, homogeneous=True)
        self.gtkLabel = gtk.Label((label + ":"))
        self.gtkLabel.set_alignment(xalign=0.0, yalign=0.5)
        self.gtkLabel.show()
        self.table.attach(self.gtkLabel, 0, 1, 0, 1)

        self.entry = gtk.Entry()
        if text != None:
            self.entry.set_text(text)
        self.entry.show()
        self.table.attach(self.entry, 1, 2, 0, 1)
        self.table.show()

    def set_value(self, value):
        self.entry.set_text(value)

    def get_value(self):
        return self.entry.get_text()

    def get_widget(self):
        return self.table, self.entry

    def set_color(self, red, blue, green):
        self.entry.modify_base(gtk.STATE_NORMAL, \
            gtk.gdk.Color(red, blue, green))

    def grab_focus(self):
        self.entry.grab_focus()


class PasswordEntry():

    def __init__(self, label, text=None):
        self.table = gtk.Table(rows=1, columns=2, homogeneous=True)
        self.gtkLabel = gtk.Label((label + ":"))
        self.gtkLabel.set_alignment(xalign=0.0, yalign=0.5)
        self.gtkLabel.show()
        self.table.attach(self.gtkLabel, 0, 1, 0, 1)

        self.entry = gtk.Entry()
        self.entry.set_visibility(False)
        if text != None:
            self.entry.set_text(text)
        self.entry.show()
        self.table.attach(self.entry, 1, 2, 0, 1)
        self.table.show()

    def set_value(self, value):
        self.entry.set_text(value)

    def get_value(self):
        return self.entry.get_text()

    def get_widget(self):
        return self.table, self.entry

    def set_color(self, red, blue, green):
        self.entry.modify_base(gtk.STATE_NORMAL, \
            gtk.gdk.Color(red, blue, green))

    def grab_focus(self):
        self.entry.grab_focus()


class Spinbutton():

    def __init__(self, label, value=1, lower=1, upper=100, \
                    step_incr=1, page_incr=10, page_size=0):
        self.table = gtk.Table(rows=1, columns=2, homogeneous=True)
        self.gtkLabel = gtk.Label((label + ":"))
        self.gtkLabel.set_alignment(xalign=0.0, yalign=0.5)
        self.gtkLabel.show()
        self.table.attach(self.gtkLabel, 0, 1, 0, 1)

        adjustment = gtk.Adjustment(value, lower, upper, \
                        step_incr, page_incr, page_size)
        self.spinbutton = gtk.SpinButton(adjustment)
        self.spinbutton.show()
        self.table.attach(self.spinbutton, 1, 2, 0, 1)
        self.table.show()

    def set_value(self, value):
        self.spinbutton.set_value(value)

    def get_value(self):
        return self.spinbutton.get_value()

    def get_widget(self):
        return self.table, self.spinbutton

    def set_color(self, red, blue, green):
        self.spinbutton.modify_base(gtk.STATE_NORMAL, \
                    gtk.gdk.Color(red, blue, green))

    def grab_focus(self):
        self.spinbutton.grab_focus()


class CheckButton():

    def __init__(self, label, value=False):
        self.table = gtk.Table(rows=1, columns=2, homogeneous=True)
        self.gtkLabel = gtk.Label((label + ":"))
        self.gtkLabel.set_alignment(xalign=0.0, yalign=0.5)
        self.gtkLabel.show()
        self.table.attach(self.gtkLabel, 0, 1, 0, 1)

        self.checkbutton = gtk.CheckButton()
        self.checkbutton.set_active(value)
        self.checkbutton.show()
        self.table.attach(self.checkbutton, 1, 2, 0, 1)
        self.table.show()

    def set_value(self, value):
        self.checkbutton.set_active(value)

    def get_value(self):
        return self.checkbutton.get_active()

    def get_widget(self):
        return self.table, self.checkbutton

    def set_color(self, red, blue, green):
        self.checkbutton.modify_base(gtk.STATE_NORMAL, \
                        gtk.gdk.Color(red, blue, green))

    def grab_focus(self):
        self.checkbutton.grab_focus()


class FileChooser():

    def __init__(self, label, value=False):
        self.table = gtk.Table(rows=2, columns=1, homogeneous=True)
        self.gtkLabel = gtk.Label((label + ":"))
        self.gtkLabel.set_alignment(xalign=0.0, yalign=0.5)
        self.gtkLabel.show()
        self.table.attach(self.gtkLabel, 0, 1, 0, 1)

        self.filechooser = gtk.FileChooserButton(_("Choose a file"))
        self.filechooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        self.filechooser.set_filename(os.environ['HOME'])
        self.filechooser.show()
        self.table.attach(self.filechooser, 0, 1, 1, 2)
        self.table.show()

    def set_value(self, value):
        self.filechooser.set_filename(value)

    def get_value(self):
        return self.filechooser.get_filename()

    def get_widget(self):
        return self.table, self.filechooser

    def set_color(self, red, blue, green):
        self.filechooser.modify_base(gtk.STATE_NORMAL, \
                        gtk.gdk.Color(red, blue, green))

    def grab_focus(self):
        self.filechooser.grab_focus()


class FolderChooser():

    def __init__(self, label, value=False):
        self.table = gtk.Table(rows=2, columns=1, homogeneous=True)
        self.gtkLabel = gtk.Label((label + ":"))
        self.gtkLabel.set_alignment(xalign=0.0, yalign=0.5)
        self.gtkLabel.show()
        self.table.attach(self.gtkLabel, 0, 1, 0, 1)

        self.dirchooser = gtk.FileChooserButton(_("Choose a directory"))
        self.dirchooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        self.dirchooser.set_filename(os.environ['HOME'])
        self.dirchooser.show()
        self.table.attach(self.dirchooser, 0, 1, 1, 2)
        self.table.show()

    def set_value(self, value):
        self.dirchooser.set_filename(value)

    def get_value(self):
        return self.dirchooser.get_filename()

    def get_widget(self):
        return self.table, self.dirchooser

    def set_color(self, red, blue, green):
        self.dirchooser.modify_base(gtk.STATE_NORMAL, \
                        gtk.gdk.Color(red, blue, green))

    def grab_focus(self):
        self.dirchooser.grab_focus()


class Scale():

    def __init__(self, label, value=0, lower=0, upper=100, \
                   step_incr=1.0, page_incr=1.0, page_size=10):
        self.table = gtk.Table(rows=2, columns=1, homogeneous=False)

        self.gtkLabel = gtk.Label((label + ":"))
        self.gtkLabel.set_alignment(xalign=0.0, yalign=0.5)
        self.gtkLabel.show()
        self.table.attach(self.gtkLabel, 0, 1, 0, 1)

        self.value = value
        self.lower = lower
        self.upper = upper
        self.step_incr = step_incr
        self.page_incr = page_incr
        self.page_size = page_size

        _adjustment = gtk.Adjustment(value, lower, upper, \
                            step_incr, page_incr, page_size)
        self.scale = gtk.HScale(adjustment=_adjustment)
        self.scale.set_digits(1)
        self.scale.set_value_pos(gtk.POS_RIGHT)
        self.scale.show()
        self.table.attach(self.scale, 0, 1, 1, 2)
        self.table.show()

    def set_value(self, value):
        _adjustment = gtk.Adjustment(value, self.lower, self.upper, \
                       self.step_incr, self.page_incr, self.page_size)
        self.scale.set_adjustment(_adjustment)

    def get_value(self):
        return self.scale.get_value()

    def get_widget(self):
        return self.table, self.scale

    def set_color(self, red, blue, green):
        self.scale.modify_base(gtk.STATE_NORMAL, \
                 gtk.gdk.Color(red, blue, green))

    def grab_focus(self):
        self.scale.grab_focus()


class RemoveDialog():

    def __init__(self, title, text):
        dialog = gtk.Dialog(title, None, gtk.DIALOG_MODAL | \
            gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_DESTROY_WITH_PARENT, None)
        #HIG tricks
        dialog.set_has_separator(False)

        dialog.add_button(gtk.STOCK_REMOVE, 3)
        dialog.add_button(gtk.STOCK_CANCEL, -1)

        dialog.label_hbox = gtk.HBox(spacing=6)

        icon = gtk.Image()
        icon.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
        dialog.label_hbox.pack_start(icon, True, True, 6)
        icon.show()

        text = text.replace("&", "&amp;")
        label = gtk.Label(text)
        label.set_use_markup(True)
        dialog.label_hbox.pack_start(label, True, True, 6)
        label.show()

        dialog.vbox.pack_start(dialog.label_hbox, True, True, 12)
        dialog.label_hbox.show()

        icon = gtk.gdk.pixbuf_new_from_file(spectlib.util.get_path() \
                                        + 'icons/specto_window_icon.svg')
        dialog.set_icon(icon)
        self.dialog = dialog

    def show(self):
        answer = self.dialog.run()
        if answer == 3:
            self.dialog.destroy()
            return True
        else:
            self.dialog.destroy()
            return False


class ErrorDialog():

    def __init__(self, specto, error_message):
        self.specto = specto
        gladefile = os.path.join(self.specto.PATH, "glade/notifier.glade")
        windowname = "error_dialog"
        self.wTree = gtk.glade.XML(gladefile, windowname, \
                                self.specto.glade_gettext)

        dic = {"on_send_clicked": self.send,
        "on_ok_clicked": self.delete_event}
        #attach the events
        self.wTree.signal_autoconnect(dic)

        self.error_dialog = self.wTree.get_widget("error_dialog")
        self.error_dialog.show()
        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.error_dialog.set_icon(icon)

        self.errorwindow = gtk.TextBuffer(None)
        self.wTree.get_widget("error_message").set_buffer(self.errorwindow)
        self.errorwindow.set_text(error_message)

        self.wTree.get_widget("image").set_from_stock(gtk.STOCK_DIALOG_ERROR, \
                                                         gtk.ICON_SIZE_DIALOG)

        self.wTree.get_widget("label4").set_use_markup(True)
        self.wTree.get_widget("label4").set_label(_("<b>Specto encountered an error</b>\nPlease verify if this bug has been entered in our issue tracker, and if not, file a bug report so we can fix it."))

    def send(self, *args):
        url = "http://code.google.com/p/specto/issues/list"
        os.system(spectlib.util.return_webpage(url) + " &")

    def delete_event(self, widget, *args):
        """ Destroy the window. """
        self.error_dialog.destroy()
        return True


def create_widget(table, widget_type, value, label, position):
    i = position
    watch_options = {}

    if not widget_type == "scale":
        gtkLabel = gtk.Label((label + ":"))
        gtkLabel.set_alignment(xalign=0.0, yalign=0.5)
        gtkLabel.show()
        table.attach(gtkLabel, 0, 1, i, i + 1)

    if widget_type == "entry":
        entry = gtk.Entry()
        entry.show()
        watch_options.update({value: entry})
        table.attach(entry, 1, 2, i, i + 1)
    elif widget_type == "password":
        entry = gtk.Entry()
        entry.set_visibility(False)
        entry.show()
        watch_options.update({value: entry})
        table.attach(entry, 1, 2, i, i + 1)
    elif widget_type == "scale":
        scale_table = gtk.Table(rows=2, columns=1, homogeneous=False)

        adjustment_label = gtk.Label((label + ":"))
        adjustment_label.set_alignment(xalign=0.0, yalign=0.5)
        adjustment_label.show()
        scale_table.attach(adjustment_label, 0, 1, 0, 1)

        _adjustment = gtk.Adjustment(value=2.0, lower=0, upper=50, \
                        step_incr=0.1, page_incr=1.0, page_size=10)
        scale = gtk.HScale(adjustment=_adjustment)
        scale.set_digits(1)
        scale.set_value_pos(gtk.POS_RIGHT)
        scale.show()
        scale_table.attach(scale, 0, 1, 1, 2)

        watch_options.update({value: scale})
        scale_table.show()
        table.attach(scale_table, 0, 2, i, i + 1)
    elif widget_type == "checkbox":
        checkbox = gtk.CheckButton()
        checkbox.show()
        watch_options.update({value: checkbox})
        table.attach(checkbox, 1, 2, i, i + 1)
    elif widget_type == "filechooser":
        filechooser = gtk.FileChooserButton(_("Choose a file"))
        filechooser.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)
        filechooser.show()
        watch_options.update({value: filechooser})
        table.attach(filechooser, 1, 2, i, i + 1)
    elif widget_type == "dirchooser":
        dirchooser = gtk.FileChooserButton(_("Choose a directory"))
        dirchooser.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        dirchooser.show()
        watch_options.update({value: dirchooser})
        table.attach(dirchooser, 1, 2, i, i + 1)
    elif widget_type == "calendar":
        calendar = gtk.Calendar()
        #calendar.show()
        watch_options.update({value: calendar})
        table.attach(calendar, 1, 2, i, i + 1)
    elif widget_type == "time":
        time_table = gtk.Table(rows=1, columns=2, homogeneous=False)
        minutes_adjustment = gtk.Adjustment(value=1, lower=1, upper=60, \
                                step_incr=1, page_incr=10, page_size=0)
        hours_adjustment = gtk.Adjustment(value=1, lower=1, upper=24, \
                                  step_incr=1, page_incr=10, page_size=0)
        hours = gtk.SpinButton(hours_adjustment)
        hours.show()
        minutes = gtk.SpinButton(minutes_adjustment)
        minutes.show()
        time_table.attach(hours, 1, 2, 1, 2)
        time_table.attach(minutes, 2, 3, 1, 2)
        #time_table.show()
        watch_options.update({value: (hours, minutes)})
        table.attach(time_table, 1, 2, i, i + 1)

    return watch_options, table


def set_widget_value(widget_type, widget, value):
    if widget_type == "entry" or widget_type == "password":
        widget.set_text(value)
    elif widget_type == "scale":
        _adjustment = gtk.Adjustment(value=value * 100, lower=0, \
                upper=50, step_incr=0.1, page_incr=1.0, page_size=10)
        widget.set_adjustment(_adjustment)
    elif widget_type == "checkbox":
        if value == "True" or value == True:
            widget.set_active(1)
        else:
            widget.set_active(0)
    elif widget_type == "filechooser" or widget_type == "dirchooser":
        widget.set_filename(value)
    elif widget_type == "calendar":
        try: #if value = string
            value = value.replace("(", "")
            value = value.replace(")", "")
            value = value.split(",")
        except: # value = tuple
            pass
        widget.select_month(int(value[1]), int(value[0]))
        widget.select_day(int(value[2]))
    elif widget_type == "time":
        widget[0].set_value(int(value[0]))
        widget[1].set_value(int(value[1]))


def get_widget_value(widget_type, value):
    result = ""
    if widget_type == "entry" or widget_type == "password":
        result = value.values()[0].get_text()
    elif widget_type == "scale":
        result = value.values()[0].get_value()
    elif widget_type == "checkbox":
        result = value.values()[0].get_active()
    elif widget_type == "filechooser" or widget_type == "dirchooser":
        result = value.values()[0].get_filename()
    elif widget_type == "calendar":
        result = value.values()[0].get_date()
    elif widget_type == "time":
        result = (value.values()[0][0].get_value(), \
                    value.values()[0][1].get_value())

    return result
