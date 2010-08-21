# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       add_watch.py
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
from spectlib.i18n import _
try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

try:
    import gtk
    import gtk.glade
    import spectlib.gtkconfig
except:
    pass


class Edit_watch:
    """Class to create the edit watch dialog."""
    # Please do not use confusing widget names such as 'lbl' and 'tbl',
    # use full names like 'label' and 'table'.
    def __init__(self, specto, notifier, id):
        self.specto = specto
        self.notifier = notifier
        self.watch = self.specto.watch_db[id]
        # Create the tree
        gladefile = os.path.join(self.specto.PATH, "glade/edit_watch.glade")
        windowname = "edit_watch"
        self.wTree = gtk.glade.XML(gladefile, windowname, self.specto.glade_gettext)

        # Catch some events
        dic = {"on_button_cancel_clicked": self.cancel_clicked,
            "on_button_save_clicked": self.save_clicked,
            "on_button_remove_clicked": self.remove_clicked,
            #"on_button_clear_clicked": self.clear_clicked,  # clear error_log textfield
            "on_button_save_as_clicked": self.save_as_clicked,  # save error_log text
            "on_edit_watch_delete_event": self.delete_event,
            "check_command_toggled": self.command_toggled,
            "check_open_toggled": self.open_toggled,
            "on_refresh_unit_changed": self.set_refresh_values}

        # Attach the events
        self.wTree.signal_autoconnect(dic)

        # Set the info from the watch
        self.edit_watch = self.wTree.get_widget("edit_watch")
        self.edit_watch.set_title(_("Edit watch: ") + self.watch.name)
        self.wTree.get_widget("name").set_text(self.watch.name)
        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.edit_watch.set_icon(icon)
        self.edit_watch.set_resizable(False)

        refresh, refresh_unit = self.specto.watch_db.get_interval(self.watch.refresh)
        self.wTree.get_widget("refresh_unit").set_active(refresh_unit)
        self.wTree.get_widget("refresh").set_value(refresh)

        # Create the gui
        self.watch_options = {}
        self.create_edit_gui()

        if not self.specto.DEBUG:
            self.wTree.get_widget("notebook1").remove_page(2)
        else:
            if self.wTree.get_widget("notebook1").get_n_pages() == 3:
                # Put the logfile in the textview
                log_text = self.specto.logger.watch_log(self.watch.name)
                self.log_buffer = self.wTree.get_widget("error_log").get_buffer()
                self.log_buffer.create_tag("ERROR", foreground="#a40000")
                self.log_buffer.create_tag("INFO", foreground="#4e9a06")
                self.log_buffer.create_tag("WARNING", foreground="#c4a000")
                iter = self.log_buffer.get_iter_at_offset(0)
                for line in log_text:
                    self.log_buffer.insert_with_tags_by_name(iter, line[1], line[0])

    def cancel_clicked(self, widget):
        """ Destroy the edit watch dialog. """
        self.edit_watch.destroy()

    def set_refresh_values(self, widget):
        """ Set the max and min values for the refresh unit. """
        digits = 0
        climb_rate = 1.0
        refresh_unit = self.wTree.get_widget("refresh_unit").get_active()

        if refresh_unit == 0 or refresh_unit == 1:
            adjustment = gtk.Adjustment(value=1, lower=1, upper=60, step_incr=1, page_incr=10, page_size=0)
        if refresh_unit == 2:
            adjustment = gtk.Adjustment(value=1, lower=1, upper=24, step_incr=1, page_incr=10, page_size=0)
        if refresh_unit == 3:
            adjustment = gtk.Adjustment(value=1, lower=1, upper=365, step_incr=1, page_incr=30, page_size=0)

        self.wTree.get_widget("refresh").configure(adjustment, climb_rate, digits)

    def save_clicked(self, widget):
        """ Save the new options from the edited watch. """
        values = {}
        #get the standard options from a watch
        values['name'] = self.wTree.get_widget("name").get_text()#FIXME: cfgparse cannot have single quotes (') it seems. We must watch out for the watch name or arguments not to have them.

        values['type'] = self.watch.type
        refresh_value = self.wTree.get_widget("refresh").get_value_as_int()
        refresh_unit = self.wTree.get_widget("refresh_unit").get_active()
        values['refresh'] = self.specto.watch_db.set_interval(refresh_value, refresh_unit)
        values['active'] = self.watch.active
        values['last_changed'] = self.watch.last_changed

        if self.wTree.get_widget("check_command").get_active() == True:
            values['command'] = self.wTree.get_widget("entry_changed_command").get_text()

        if self.wTree.get_widget("check_open").get_active() == True:
            values['open_command'] = self.wTree.get_widget("entry_open_command").get_text()
        else:
            values['open_command'] = ""

        gui_values = self.specto.watch_db.plugin_dict[values['type']].get_add_gui_info()
        window_options = self.watch_options[values['type']]

        for key in window_options:
            values[key] = window_options[key].get_value()
            window_options[key].set_color(0xFFFF, 0xFFFF, 0xFFFF)

        self.wTree.get_widget("name").modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0xFFFF, 0xFFFF, 0xFFFF))

        try:
            self.specto.watch_db[self.watch.id].set_values(values, True)
        except AttributeError, error_fields:
            fields = str(error_fields).split(",")
            i = 1
            for field in fields:
                if field == " name":
                    self.wTree.get_widget("name").modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 0, 0))
                    self.wTree.get_widget("name").grab_focus()
                else:
                    field = window_options[field.strip()]
                    if i == 1:
                        field.grab_focus()
                        i = 0
                    field.set_color(65535, 0, 0)
        else:
            if not self.specto.watch_io.is_unique_watch(values['name']):
                self.specto.watch_io.replace_name(self.watch.name, values['name'])
                # Change the name in the notifier window
                self.specto.notifier.change_name(values['name'], self.watch.id)

            self.specto.watch_db[self.watch.id].set_values(values)

            self.specto.watch_io.write_watch(values)
            self.specto.notifier.show_watch_info()
            self.edit_watch.destroy()

            if self.watch.active == True:
                self.specto.watch_db[self.watch.id].restart()

    def remove_clicked(self, widget):
        """ Remove the watch. """
        dialog = spectlib.gtkconfig.RemoveDialog(_("Remove a watch"),
        (_('<big>Remove the watch "%s"?</big>\nThis operation cannot be undone.') % self.watch.name))
        answer = dialog.show()
        if answer == True:
            self.edit_watch.destroy()
            self.notifier.remove_notifier_entry(self.watch.id)
            self.specto.watch_db.remove(self.watch.id) #remove the watch
            self.specto.watch_io.remove_watch(self.watch.name)
            self.notifier.tray.show_tooltip()

    def clear_clicked(self, widget):
        """ Clear the log window. """
        self.specto.logger.remove_watch_log(self.watch.name)
        self.log = self.specto.logger.watch_log(self.watch.name)
        self.logwindow.set_text(self.log)

    def save_as_clicked(self, widget):
        """ Open the Save as dialog window. """
        Save_dialog(self, self.log)

    def delete_event(self, widget, event, data=None):
        """ Destroy the window. """
        self.edit_watch.destroy()
        return True

    def create_edit_gui(self):
        """ Create the gui for the different kinds of watches. """
        vbox_options = self.wTree.get_widget("vbox_watch_options")
        try:
            self.table.destroy()
        except:
            pass

        watch_type = self.watch.type
        values = self.specto.watch_db.plugin_dict[watch_type].get_add_gui_info()
        watch_values = self.watch.get_values()

        if watch_values['command'] != "":
            self.wTree.get_widget("entry_changed_command").set_text(watch_values['command'])
            self.wTree.get_widget("check_command").set_active(True)
        else:
            self.wTree.get_widget("entry_changed_command").set_text("")
            self.wTree.get_widget("check_command").set_active(False)

        if watch_values['open_command'] != "":
            self.wTree.get_widget("entry_open_command").set_text(watch_values['open_command'])
            self.wTree.get_widget("check_open").set_active(True)
        else:
            self.wTree.get_widget("entry_open_command").set_text("")
            self.wTree.get_widget("check_open").set_active(False)


        # Create the options gui
        self.table = gtk.Table(rows=len(values), columns=2, homogeneous=False)
        self.table.set_row_spacings(6)
        self.table.set_col_spacings(6)
        self.watch_options[watch_type] = {}

        i = 0
        for value, widget in values:
            table, _widget = widget.get_widget()
            widget.set_value(watch_values[value])
            self.table.attach(table, 0, 1, i, i + 1)
            self.watch_options[watch_type].update({value: widget})
            i += 1

        self.table.show()
        vbox_options.pack_start(self.table, False, False, 0)

    def command_toggled(self, widget):
        sensitive = self.wTree.get_widget("check_command").get_active()
        self.wTree.get_widget("entry_changed_command").set_sensitive(sensitive)

    def open_toggled(self, widget):
        sensitive = self.wTree.get_widget("check_open").get_active()
        self.wTree.get_widget("entry_open_command").set_sensitive(sensitive)


class Save_dialog:
    """
    Class to create the save dialog.
    """

    def __init__(self, specto, *args):
        """ Display the save as dialog. """
        self.specto = specto
        self.text = args[0]
        # Create the tree
        gladefile = os.path.join(self.specto.PATH, "glade/edit_watch.glade")
        windowname = "file_chooser"
        self.wTree = gtk.glade.XML(gladefile, windowname)
        self.save_dialog = self.wTree.get_widget("file_chooser")

        dic = {"on_button_cancel_clicked": self.cancel,
            "on_button_save_clicked": self.save}
        # Attach the events
        self.wTree.signal_autoconnect(dic)

        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.save_dialog.set_icon(icon)
        self.save_dialog.set_filename(os.environ['HOME'] + "/ ")

    def cancel(self, *args):
        """ Destroy the window. """
        self.save_dialog.destroy()

    def save(self, *args):
        """ Save the file. """
        file_name = self.save_dialog.get_filename()

        f = open(file_name, "w")
        f.write(self.text)
        f.close()

        self.save_dialog.destroy()


if __name__ == "__main__":
    # Run the gui
    app = Edit_watch()
    gtk.main()
