# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       notifier.py
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
from random import randrange
from datetime import datetime

from spectlib.preferences import Preferences
from spectlib.add_watch import Add_watch
from spectlib.about import About
from spectlib.edit_watch import Edit_watch
from spectlib.logger import Log_dialog
from spectlib.balloons import NotificationToast
from spectlib.import_watch import Import_watch
from spectlib.export_watch import Export_watch
from spectlib.trayicon import Tray


import spectlib.util
from spectlib.gtkconfig import ErrorDialog
from spectlib.i18n import _

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

try:
    import gtk
    import gtk.glade
    import gobject
    import pango
    import gnome
except:
    pass


class Notifier:
    """
    Class to create the main specto window
    """
    add_w = ""
    edit_w = ""
    error_l = ""
    about = ""
    export_watch = ""
    import_watch = ""

    def __init__(self, specto):
        """
        In this init we are going to display the main notifier window.
        """
        self.specto = specto
        self.tray = Tray(specto, self)
        self.balloon = NotificationToast(specto, self)
        self.preferences_initialized = False
        gnome.sound_init('localhost')

        #create tree
        self.iter = {}
        gladefile = os.path.join(self.specto.PATH, "glade/notifier.glade")
        windowname = "notifier"
        self.wTree = gtk.glade.XML(gladefile, windowname, self.specto.glade_gettext)
        self.model = gtk.ListStore(gobject.TYPE_BOOLEAN, gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, pango.Weight)

        #catch some events
        dic = {
        "on_add_activate": self.show_add_watch_menu,
        "on_edit_activate": self.show_edit_watch,
        "on_clear_all_activate": self.mark_all_as_read,
        "on_preferences_activate": self.show_preferences,
        "on_refresh_activate": self.refresh_all_watches,
        "on_close_activate": self.delete_event,
        "on_import_watches_activate": self.import_watches,
        "on_export_watches_activate": self.export_watches,
        "on_error_log_activate": self.show_error_log,
        "on_display_all_watches_activate": self.toggle_show_deactivated_watches,
        "on_display_toolbar_activate": self.toggle_display_toolbar,
        "on_help_activate": self.show_help,
        "on_about_activate": self.show_about,
        "on_treeview_row_activated": self.open_watch_callback,
        "on_btnOpen_clicked": self.open_watch_callback,
        "on_btnClear_clicked": self.mark_watch_as_read,
        "on_treeview_cursor_changed": self.show_watch_info,
        "on_btnEdit_clicked": self.show_edit_watch,
        "on_by_watch_type_activate": self.sort_type,
        "on_by_name_activate": self.sort_name,
        "on_by_watch_active_activate": self.sort_active,
        "on_remove_clicked": self.remove_watch,
        "on_clear_activate": self._mark_watch_as_read,
        "on_remove_activate": self.remove_watch}
        self.wTree.signal_autoconnect(dic)

        self.notifier = self.wTree.get_widget("notifier")
        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.svg"))
        self.notifier.set_icon(icon)
        self.specto.notifier_initialized = True
        self.create_notifier_gui()
        self.stop_refresh = False

    def mark_watch_as_read(self, widget, *id):
        """
        Call the main function to mark the watch as read and reset the name in the notifier.
        If widget == '' then id will be used to mark the watch as read else the selected watch will be marked as read.
        """
        try:
            id = id[0]
        except:
            model, iter = self.treeview.get_selection().get_selected()
            id = int(model.get_value(iter, 3))
        watch = self.specto.watch_db[id]
        watch.mark_as_read()
        self.model.set(self.iter[id], 2, watch.name, 5, pango.WEIGHT_NORMAL)
        if self.model.iter_is_valid(self.iter[id]) and not watch.error:
            self.model.set_value(self.iter[id], 1, self.get_icon(watch.icon, 50, False))
        if watch.changed == False:
            self.wTree.get_widget("btnClear").set_sensitive(False)
        else:
            self.wTree.get_widget("btnClear").set_sensitive(True)
        #check if all watches has been marked as read
        changed_watches = False
        changes = self.specto.watch_db.count_changed_watches()
        for changed in changes.values():
            if changed > 0:
                changed_watches = True
        if changed_watches == False:
            self.wTree.get_widget("button_clear_all").set_sensitive(False)

    def mark_all_as_read(self, widget):
        """ Call the main function to mark all watches as read and reset the name in the notifier. """
        self.wTree.get_widget("btnClear").set_sensitive(False)
        self.wTree.get_widget("button_clear_all").set_sensitive(False)
        self.wTree.get_widget("clear_all1").set_sensitive(False)
        for watch in self.specto.watch_db:
            if self.model.iter_is_valid(self.iter[watch.id]):
                self.mark_watch_as_read("", watch.id)

    def refresh_all_watches(self, *widget):
        """ Call the main funcion to refresh all active watches and change refresh icon to stop. """
        if self.wTree.get_widget("button_refresh").get_stock_id() == "gtk-refresh":
            self.wTree.get_widget("button_refresh").set_stock_id("gtk-stop") #menu item, does not allow changing label
            self.wTree.get_widget("button_refresh").set_label(_("Stop"))
            self.wTree.get_widget("button_add").set_sensitive(False)
            self.wTree.get_widget("btnEdit").set_sensitive(False)
            for i in self.iter:
                if self.stop_refresh == True:
                    self.stop_refresh = False
                    break
                try:
                    iter = self.model.get_iter(i)
                    if self.model.iter_is_valid(iter):
                        model = self.model
                        id = int(model.get_value(iter, 3))
                except:
                    break
                if self.specto.watch_db[id].active == True:
                    try:
                        self.specto.watch_db[id].stop()
                    except:
                        pass
                    self.specto.watch_db[id].start()
            self.wTree.get_widget("button_refresh").set_stock_id("gtk-refresh") #menu item, does not allow changing label
            self.wTree.get_widget("button_refresh").set_label(_("Refresh All"))
            self.wTree.get_widget("button_add").set_sensitive(True)
            self.wTree.get_widget("btnEdit").set_sensitive(True)
        else:
            self.stop_refresh = True

    def mark_error(self, error_message):
        error_dialog = ErrorDialog(self.specto, error_message)

    def mark_watch_status(self, status, id):
        """ show the right icon for the status from the watch. """
        watch = self.specto.watch_db[id]
        statusbar = self.wTree.get_widget("statusbar1")
        icon = self.get_icon("error", 50, False)

        try:
            if status == "checking":
                icon = self.get_icon("reload", 0, False)
                statusbar.push(0, (datetime.today().strftime("%H:%M") + " - " + _('The watch "%s" is checking.') % watch.name))

            elif status == "idle":
                self.tray.show_tooltip() #check if all watches are cleared
                if watch.changed == True:
                    self.model.set(self.iter[id], 2, "%s" % watch.name, 5, pango.WEIGHT_BOLD)
                    self.wTree.get_widget("button_clear_all").set_sensitive(True)
                    self.wTree.get_widget("clear_all1").set_sensitive(True)
                    icon = self.get_icon(watch.icon, 0, False)
                else:
                    self.model.set(self.iter[id], 2, "%s" % watch.name, 5, pango.WEIGHT_NORMAL)
                    self.wTree.get_widget("clear_all1").set_sensitive(False)
                    icon = self.get_icon(watch.icon, 50, False)
                statusbar.push(0, "")  # As per HIG, make the status bar empty when nothing is happening
            elif status == "no-network":
                statusbar.push(0, (datetime.today().strftime("%H:%M") + " - " + _('The network connection seems to be down, networked watches will not check until then.')))
                self.tray.show_tooltip()
                icon = self.get_icon(watch.icon, 50, False)

            elif status == "error":
                statusbar.push(0, (datetime.today().strftime("%H:%M") + " - " + _('The watch "%s" has a problem.') % watch.name))
                balloon_icon = self.get_icon("error", 0, True)
                icon = self.get_icon("error", 50, False)
                if self.specto.specto_gconf.get_entry("pop_toast") == True:
                    self.balloon.show_toast(watch.error_message, balloon_icon, urgency="critical", summary=(_("%s encountered a problem") % watch.name))
                if self.specto.specto_gconf.get_entry("use_problem_sound"):
                    problem_sound = self.specto.specto_gconf.get_entry("problem_sound")
                    gnome.sound_play(problem_sound)

            elif status == "changed":
                statusbar.push(0, (datetime.today().strftime("%H:%M") + " - " + _('The watch "%s" has changed.') % watch.name))

                self.model.set(self.iter[id], 2, "%s" % watch.name, 5, pango.WEIGHT_BOLD)

                self.wTree.get_widget("button_clear_all").set_sensitive(True)
                self.wTree.get_widget("clear_all1").set_sensitive(True)

                if self.model.iter_is_valid(self.iter[id]):
                    icon = self.get_icon(watch.icon, 0, False)

                self.tray.show_tooltip()

                balloon_icon = self.get_icon(watch.icon, 0, True)
                if self.specto.specto_gconf.get_entry("pop_toast") == True:
                    self.balloon.show_toast(watch.get_balloon_text(), balloon_icon, summary=(_("%s has changed") % watch.name), name=watch.name)

                icon = self.get_icon(watch.icon, 0, False)
                if self.specto.specto_gconf.get_entry("use_changed_sound"):
                    changed_sound = self.specto.specto_gconf.get_entry("changed_sound")
                    gnome.sound_play(changed_sound)

            self.model.set_value(self.iter[id], 1, icon)

            try:
                model, iter = self.treeview.get_selection().get_selected()
                id2 = int(model.get_value(iter, 3))
                if id == id2:
                    self.show_watch_info()
            except:
                pass
        except:
            self.specto.logger.log(_("There was an error marking the watch status"), "error", watch.name)

    def deactivate(self, id):
        """ Disable the checkbox from the watch. """
        watch = self.specto.watch_db[id]
        self.model.set_value(self.iter[id], 0, 0)#TODO: make the text label in the "Name" column and the buttons insensitive

    def activate(self, id):
        """ enable the checkbox from the watch. """
        watch = self.specto.watch_db[id]
        self.model.set_value(self.iter[id], 0, 1)#TODO: make the text label in the "Name" column and the buttons insensitive

    def get_icon(self, icon, percent, size):
        """ Calculate the alpha and return a transparent pixbuf. The input percentage is the 'transparency' percentage. 0 means no transparency. """
        if icon == "":
            icon = "dialog-information"

        if size == True:
            size = 64
        else:
            size = 22

        try:
            icon = self.specto.icon_theme.load_icon(icon, size, 0)
        except gobject.GError:
            try:
                icon = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(self.specto.PATH, ("icons/" + icon + ".svg")), size, size)
            except:
                icon = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(self.specto.PATH, "icons/specto_tray_1.svg"), size, size)

        icon = icon.add_alpha(False, '0', '0', '0')
        for row in icon.get_pixels_array():
            for pix in row:
                pix[3] = min(int(pix[3]), 255 - (percent * 0.01 * 255))#note: we must *0.01, NOT /100, otherwise it won't work
        return icon

    def add_notifier_entry(self, id):
        """ Add an entry to the notifier list. """
        watch = self.specto.watch_db[id]
        if watch.active == True:
            active = 1
        else:
            active = 0

        self.iter[id] = self.model.insert_before(None, None)
        self.model.set_value(self.iter[id], 0, active)
        self.model.set_value(self.iter[id], 1, self.get_icon(watch.icon, 50, False))
        self.model.set_value(self.iter[id], 2, watch.name)
        self.model.set_value(self.iter[id], 3, watch.id)
        self.model.set_value(self.iter[id], 4, watch.type)
        self.model.set(self.iter[id], 5, pango.WEIGHT_NORMAL)#make sure the text is not fuzzy on startup

        if not self.wTree.get_widget("display_all_watches").active and active == 0: #dont creat the entry
            self.remove_notifier_entry(id)

    def remove_notifier_entry(self, id):
        path = self.model.get_path(self.iter[id])
        iter = self.model.get_iter(path)
        id = int(self.model.get_value(iter, 3))
        self.model.remove(iter)

    def check_clicked(self, object, path, model):
        """ Call the main function to start/stop the selected watch. """
        sel = self.treeview.get_selection()
        sel.select_path(path)

        model, iter = self.treeview.get_selection().get_selected()
        id = int(model.get_value(iter, 3))
        watch = self.specto.watch_db[id]

        if model.get_value(iter, 0):
            model.set_value(iter, 0, 0)
            if watch.changed:
                self.mark_watch_as_read("", id)
            self.mark_watch_status("idle", id)
            watch.stop()
            if not self.wTree.get_widget("display_all_watches").active:
                self.remove_notifier_entry(id)
        else:
            model.set_value(iter, 0, 1)
            watch.start()

    def connected_message(self, connected):
        return
        if not connected:
            self.wTree.get_widget("statusbar1").push(0, _("The network connection seems to be down, networked watches will not check until then."))
            self.wTree.get_widget("statusbar1").show()
        else:
            self.wTree.get_widget("statusbar1").hide()

    def show_watch_info(self, *args):
        """ Show the watch information in the notifier window. """
        model, iter = self.treeview.get_selection().get_selected()

        if iter != None and self.model.iter_is_valid(iter):
            self.wTree.get_widget("edit").set_sensitive(True)
            self.wTree.get_widget("remove").set_sensitive(True)

            if not self.info_table.flags() & gtk.VISIBLE:
                #hide the tip of the day and show the buttons
                self.quicktip.hide()
                self.quicktip_image.hide()
                self.wTree.get_widget("vbox_panel_buttons").show()
                self.wTree.get_widget("notebook1").show()
                self.info_table.show()

            id = int(model.get_value(iter, 3))

            watch = self.specto.watch_db[id]
            watch_values = watch.get_gui_info()

            #set the error log field
            if not self.specto.DEBUG:
                self.wTree.get_widget("notebook1").remove_page(2)
            else:
                if self.wTree.get_widget("notebook1").get_n_pages() == 2:
                    self.wTree.get_widget("notebook1").append_page(self.error_log_window, self.label_error_log)
                log_text = self.specto.logger.watch_log(watch.name)

                start = self.log_buffer.get_start_iter()
                end = self.log_buffer.get_end_iter()
                self.log_buffer.delete(start, end)

                iter = self.log_buffer.get_iter_at_offset(0)
                for line in log_text:
                    self.log_buffer.insert_with_tags_by_name(iter, line[1], line[0])

            if watch.changed == False:
                self.wTree.get_widget("clear").set_sensitive(False)
                self.wTree.get_widget("btnClear").set_sensitive(False)
                self.wTree.get_widget("lblExtraInfo").set_label(_("No extra information available."))
            else:
                self.wTree.get_widget("clear").set_sensitive(True)
                self.wTree.get_widget("btnClear").set_sensitive(True)
                try:
                    self.extra_info = watch.get_extra_information()
                    if self.extra_info != "":
                        try:
                            self.wTree.get_widget("lblExtraInfo").set_label(self.extra_info)
                        except:
                            self.specto.logger.log(_("Extra information could not be set"), "error", self.specto.watch_db[id].name)
                except:
                    self.specto.logger.log(_("Extra information could not be set"), "error", self.specto.watch_db[id].name)

            i = 0
            while i < 4:
                if i >= len(watch_values):
                    self.info_labels[i][0].set_label("")
                    self.info_labels[i][1].set_label("")
                else:
                    #create label
                    self.info_labels[i][0].set_label("<b>" + str(watch_values[i][0]) + ":</b>")
                    label = str(watch_values[i][1]).replace("&", "&amp;")
                    self.info_labels[i][1].set_label(label)

                i += 1

            image = self.wTree.get_widget("watch_icon")
            image.set_from_pixbuf(self.get_icon(watch.icon, 0, True))

    def open_watch(self, id):
        """
        Open the selected watch.
        Returns False if the watch failed to open
        """
        res = True
        try:
            watch = self.specto.watch_db[id]
            if watch.open_command != "":
                self.specto.logger.log(_("Watch opened"), "info", self.specto.watch_db[id].name)
                os.system(watch.open_command + " &")
        except:
            res = False
        return res

    def open_watch_callback(self, *args):
        """
        Opens the selected watch and mark it as unchanged
        """
        model, iter = self.treeview.get_selection().get_selected()
        id = int(model.get_value(iter, 3))
        self.open_watch(id)
        if self.specto.watch_db[id].changed == True:
            self.mark_watch_as_read(None, id)

    def show_watch_popup(self, treeview, event, data=None):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)
                menu = self.create_menu(self, self.notifier, None)
                menu.popup(None, None, None, 3, time)
            return 1

    def _mark_watch_as_read(self, *widget):
        try:
            model, iter = self.treeview.get_selection().get_selected()
            id = int(model.get_value(iter, 3))

            self.mark_watch_as_read(id)
        except:
            pass

    def refresh_watch(self, widget):
        model, iter = self.treeview.get_selection().get_selected()
        id = int(model.get_value(iter, 3))
        watch = self.specto.watch_db[id]
        watch.restart()

    def edit_watch(self, widget):
        model, iter = self.treeview.get_selection().get_selected()
        id = int(model.get_value(iter, 3))
        self.show_edit_watch(self, widget, id)

    def create_menu(self, window, event, data=None):
        model, iter = self.treeview.get_selection().get_selected()
        id = int(model.get_value(iter, 3))
        watch = self.specto.watch_db[id]
        menu = gtk.Menu()

        menuItem = gtk.ImageMenuItem(_("Refresh"))
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU)
        menuItem.set_image(image)
        menuItem.connect('activate', self.refresh_watch)
        if watch.active == False:
            menuItem.set_sensitive(False)
        menu.append(menuItem)

        menuItem = gtk.ImageMenuItem(_("Mark as read"))
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU)
        menuItem.set_image(image)
        menuItem.connect('activate', self._mark_watch_as_read)
        if watch.changed == False:
            menuItem.set_sensitive(False)
        menu.append(menuItem)

        separator = gtk.SeparatorMenuItem()
        menu.append(separator)

        menuItem = gtk.ImageMenuItem(_("Edit"))
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU)
        menuItem.set_image(image)
        menuItem.connect('activate', self.edit_watch)
        menu.append(menuItem)

        menuItem = gtk.ImageMenuItem(_("Remove"))
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
        menuItem.set_image(image)
        menuItem.connect('activate', self.remove_watch)
        menu.append(menuItem)

        menu.show_all()
        return menu

    def change_entry_name(self, *args):
        """ Edit the name from the watch in the notifier window. """
        # Change the name in the treeview
        model, iter = self.treeview.get_selection().get_selected()
        id = int(model.get_value(iter, 3))
        self.change_name(args[2], id)

    def change_name(self, new_name, id):
        if self.specto.watch_db[id].changed == True:
            weight = pango.WEIGHT_BOLD
        else:
            weight = pango.WEIGHT_NORMAL
        self.model.set(self.iter[id], 2, new_name, 5, weight)

        # Write the new name in watches.list
        self.specto.watch_io.replace_name(self.specto.watch_db[id].name, new_name)
        # Change the name in the database
        self.specto.watch_db[id].name = new_name
        self.show_watch_info()

### GUI FUNCTIONS ###
    def get_quick_tip(self):
        """Return a random tip of the day to be shown on startup"""
        tips = [_("You can add all kinds of websites as watches. Static pages, RSS or Atom feeds, etc. Specto will automatically handle them."),
                    _("Website watches can use an error margin that allows you to set a minimum difference percentage. This allows you to adapt to websites that change constantly or have lots of advertising."),
                    _("Single-click an existing watch to display information, and double-click it to open the content."),
                    _("Please set a reasonable refresh interval in order to save bandwidth and prevent you from being blocked from content providers.")]
        chosen_tip = tips[randrange(len(tips))]
        return chosen_tip

    def toggle_display_toolbar(self, *args):
        """ Show or hide the toolbar. """
        if self.wTree.get_widget("display_toolbar").active:
            self.wTree.get_widget("toolbar").show()
            self.specto.specto_gconf.set_entry("hide_toolbar", False)
        else:
            self.wTree.get_widget("toolbar").hide()
            self.specto.specto_gconf.set_entry("hide_toolbar", True)

    def toggle_show_deactivated_watches(self, *widget):
        """ Display only active watches or all watches. """
        if self.startup != True:
            self.startup = False  # This is important to prevent *widget from messing with us. If you don't believe me, print startup ;)
        if self.startup == True:
            self.startup = False
        else:
            if self.wTree.get_widget("display_all_watches").active:
                for watch in self.specto.watch_db:
                    if watch.active == False:  # For each watch that is supposed to be inactive, show it in the notifier but don't activate it
                        if self.startup == False:  # Recreate the item because it was deleted
                            self.add_notifier_entry(watch.id)
                self.specto.specto_gconf.set_entry("show_deactivated_watches", True)
            else:  # Hide the deactivated watches
                for i in self.iter:
                    if self.model.iter_is_valid(self.iter[i]):
                        path = self.model.get_path(self.iter[i])
                        iter = self.model.get_iter(path)
                        model = self.model
                        id = int(model.get_value(iter, 3))

                        if self.specto.watch_db[id].active == False:
                            model.remove(iter)
                self.specto.specto_gconf.set_entry("show_deactivated_watches", False)

    def remove_watch(self, *widget):
        try:
            model, iter = self.treeview.get_selection().get_selected()
            id = int(model.get_value(iter, 3))
        except:
            pass
        else:
            dialog = spectlib.gtkconfig.RemoveDialog(_("Remove a watch"),
            (_('<big>Remove the watch "%s"?</big>\nThis operation cannot be undone.') % self.specto.watch_db[id].name))
            answer = dialog.show()
            if answer == True:
                self.remove_notifier_entry(id)
                self.specto.watch_db.remove(id) #remove the watch
                self.specto.watch_io.remove_watch(self.specto.watch_db[id].name)
                self.tray.show_tooltip()

    def delete_event(self, *args):
        """
        Return False to destroy the main window.
        Return True to stop destroying the main window.
        """
        self.save_size_and_position()
        if self.specto.specto_gconf.get_entry("always_show_icon") == True:
            self.notifier.hide()
            self.specto.specto_gconf.set_entry("show_notifier", False)#save the window state for the next time specto starts
            return True
        else:
            self.specto.quit()
            return True

    def restore_size_and_position(self):
        """
        Restore the size and the postition from the notifier window.
        """
        saved_window_width = self.specto.specto_gconf.get_entry("window_notifier_width")
        saved_window_height = self.specto.specto_gconf.get_entry("window_notifier_height")
        saved_window_x = self.specto.specto_gconf.get_entry("window_notifier_x")
        saved_window_y = self.specto.specto_gconf.get_entry("window_notifier_y")
        if self.specto.specto_gconf.get_entry("hide_from_windowlist")==True:
            self.notifier.set_skip_taskbar_hint(True)  # Hide from the window list applet

        if saved_window_width != None and saved_window_height != None:  # Check if the size is not 0
            self.wTree.get_widget("notifier").resize(saved_window_width, saved_window_height)

        if saved_window_x != None and saved_window_y != None:  # Check if the position is not 0
            self.wTree.get_widget("notifier").move(saved_window_x, saved_window_y)

    def save_size_and_position(self):
        """
        Save the size and position from the notifier in gconf when the window is closed.
        """
        # Save the size in gconf
        current_window_size = self.wTree.get_widget("notifier").get_size()
        current_window_width = current_window_size[0]
        current_window_height = current_window_size[1]
        self.specto.specto_gconf.set_entry("window_notifier_width", current_window_width)
        self.specto.specto_gconf.set_entry("window_notifier_height", current_window_height)

        # Save the window position in gconf when the window is closed
        current_window_xy = self.wTree.get_widget("notifier").get_position()
        current_window_x = current_window_xy[0]
        current_window_y = current_window_xy[1]
        self.specto.specto_gconf.set_entry("window_notifier_x", current_window_x)
        self.specto.specto_gconf.set_entry("window_notifier_y", current_window_y)

    def get_state(self):
        """ Return True if the notifier window is visible. """
        if self.notifier.flags() & gtk.VISIBLE:
            return True
        else:
            return False

    def create_notifier_gui(self):
        """ Create the gui from the notifier. """
        self.treeview = self.wTree.get_widget("treeview")
        self.treeview.set_model(self.model)
        self.treeview.set_flags(gtk.TREE_MODEL_ITERS_PERSIST)
        self.treeview.connect("button_press_event", self.show_watch_popup, None)
        self.wTree.get_widget("button_clear_all").set_sensitive(False)
        self.wTree.get_widget("clear_all1").set_sensitive(False)

        if self.specto.specto_gconf.get_entry("show_in_windowlist") == False:
            self.notifier.set_skip_taskbar_hint(True)


        ### Initiate the window
        self.restore_size_and_position()
        self.show_toolbar = self.specto.specto_gconf.get_entry("show_toolbar")
        if  self.show_toolbar == False:
            self.wTree.get_widget("display_toolbar").set_active(False)
            self.toggle_display_toolbar()
        else:
            self.wTree.get_widget("display_toolbar").set_active(True)
            self.toggle_display_toolbar()

        self.startup = True
        if self.specto.specto_gconf.get_entry("show_deactivated_watches") == True:
            self.wTree.get_widget("display_all_watches").set_active(True)
        else:
            self.wTree.get_widget("display_all_watches").set_active(False)
        self.startup = False

        if self.specto.specto_gconf.get_entry("show_notifier") == True:
            self.notifier.show()

        ### Checkbox
        self.columnCheck_renderer = gtk.CellRendererToggle()
        self.columnCheck_renderer.set_property("activatable", True)
        self.columnCheck_renderer.connect("toggled", self.check_clicked, self.model)
        self.columnCheck = gtk.TreeViewColumn(_("Active"), self.columnCheck_renderer, active=0)
        self.columnCheck.connect("clicked", self.sort_active_from_treeview_headers)
        self.columnCheck.set_sort_column_id(0)
        self.treeview.append_column(self.columnCheck)

        ### Icon
        self.columnIcon_renderer = gtk.CellRendererPixbuf()
        self.columnIcon = gtk.TreeViewColumn(_("Type"), self.columnIcon_renderer, pixbuf=1)
        self.columnIcon.set_clickable(True)
        self.columnIcon.connect("clicked", self.sort_type_from_treeview_headers)
        self.treeview.append_column(self.columnIcon)

        ### Titre
        self.columnTitle_renderer = gtk.CellRendererText()
        #self.columnTitle_renderer.set_property("editable", True)
        #self.columnTitle_renderer.connect('edited', self.change_entry_name)
        self.columnTitle = gtk.TreeViewColumn(_("Name"), self.columnTitle_renderer, text=2, weight=5)
        self.columnTitle.connect("clicked", self.sort_name_from_treeview_headers)
        self.columnTitle.set_expand(True)
        self.columnTitle.set_resizable(True)
        self.columnTitle.set_sort_column_id(2)
        self.treeview.append_column(self.columnTitle)

        ### ID
        self.columnID_renderer = gtk.CellRendererText()
        self.columnID = gtk.TreeViewColumn(_("ID"), self.columnID_renderer, markup=3)
        self.columnID.set_visible(False)
        self.columnID.set_sort_column_id(3)
        self.treeview.append_column(self.columnID)

        ### type
        self.renderer = gtk.CellRendererText()
        self.columnType = gtk.TreeViewColumn(_("TYPE"), self.renderer, markup=4)
        self.columnType.set_visible(False)
        self.columnType.set_sort_column_id(4)
        self.treeview.append_column(self.columnType)

        self.get_startup_sort_order()


        ###Create info-panel
        vbox_info = self.wTree.get_widget("vbox_info")

        #show tip of the day
        self.quicktip = self.get_quick_tip()
        self.quicktip_image = gtk.Image()
        self.quicktip_image.set_from_pixbuf(self.get_icon("dialog-information", 0, True))
        self.quicktip_image.show()
        vbox_info.pack_start(self.quicktip_image, False, False, 0)
        self.quicktip = gtk.Label(("<big>" + _("Tip of the Day:") + "</big> "+ self.quicktip))
        self.quicktip.set_line_wrap(True)
        self.quicktip.set_use_markup(True)
        self.quicktip.set_alignment(xalign=0.0, yalign=0.5)
        self.quicktip.show()
        vbox_info.pack_start(self.quicktip, False, False, 0)

        #create the info table
        self.info_table = gtk.Table(rows=4, columns=2, homogeneous=True)
        self.info_table.set_row_spacings(6)
        self.info_table.set_col_spacings(6)
        vbox_watch_info = self.wTree.get_widget("vbox_watch_info")
        vbox_watch_info.pack_start(self.info_table, False, False, 0)   #show the image

        i = 0
        self.info_labels = []
        while i < 4:
            gtk_label = gtk.Label()
            gtk_label.set_alignment(xalign=0.0, yalign=0.5)
            gtk_label.set_use_markup(True)
            gtk_label.set_ellipsize(pango.ELLIPSIZE_END)
            gtk_label.show()

            #create value
            gtk_label1 = gtk.Label()
            gtk_label1.set_alignment(xalign=0.0, yalign=0.5)
            gtk_label1.set_use_markup(True)
            gtk_label1.set_ellipsize(pango.ELLIPSIZE_END)
            gtk_label1.show()

            self.info_labels.extend([(gtk_label, gtk_label1)])
            self.info_table.attach(self.info_labels[i][1], 1, 2, i, i + 1)
            self.info_table.attach(self.info_labels[i][0], 0, 1, i, i + 1)

            i += 1

        #create the error log textview and notebook label
        self.error_log = gtk.TextView()
        self.log_buffer = self.error_log.get_buffer()
        self.log_buffer.create_tag("ERROR", foreground="#a40000")
        self.log_buffer.create_tag("INFO", foreground="#4e9a06")
        self.log_buffer.create_tag("WARNING", foreground="#c4a000")
        self.error_log_window = gtk.ScrolledWindow()
        self.error_log_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.error_log_window.add_with_viewport(self.error_log)
        self.error_log_window.show()
        self.label_error_log = gtk.Label(_("Error log"))
        self.error_log.show()
        self.label_error_log.show()

        #hide the buttons
        self.wTree.get_widget("vbox_panel_buttons").hide()

        self.wTree.get_widget("edit").set_sensitive(False)
        self.wTree.get_widget("clear").set_sensitive(False)
        self.wTree.get_widget("remove").set_sensitive(False)

        self.wTree.get_widget("statusbar1").show()

        self.wTree.get_widget("notebook1").hide()

        self.generate_add_menu()

### Sort functions ###
    def get_startup_sort_order(self):
        order = self.get_gconf_sort_order()
        sort_function = self.specto.specto_gconf.get_entry("sort_function")
        if  sort_function == "name":
            self.wTree.get_widget("by_name").set_active(True)
            self.model.set_sort_column_id(2, order)
        elif sort_function == "type":
            self.wTree.get_widget("by_watch_type").set_active(True)
            self.model.set_sort_column_id(4, order)
        elif sort_function == "active":
            self.wTree.get_widget("by_watch_active").set_active(True)
            self.model.set_sort_column_id(0, order)

    def get_gconf_sort_order(self):
        """ Get the order (asc, desc) from a gconf key. """
        order = self.specto.specto_gconf.get_entry("sort_order")
        if order == "asc":
            sort_order = gtk.SORT_ASCENDING
        else:
            sort_order = gtk.SORT_DESCENDING
        return sort_order

    def set_gconf_sort_order(self, order):
        """ Set the order (asc, desc) for a gconf keys. """
        if order == gtk.SORT_ASCENDING:
            sort_order = "asc"
        else:
            sort_order = "desc"
        return sort_order

    def sort_name(self, *args):
        """ Sort by watch name. """
        self.model.set_sort_column_id(2, not self.columnTitle.get_sort_order())
        self.specto.specto_gconf.set_entry("sort_function", "name")

    def sort_type(self, *args):
        """ Sort by watch type. """
        self.model.set_sort_column_id(4, not self.columnType.get_sort_order())
        self.specto.specto_gconf.set_entry("sort_function", "type")
        self.specto.specto_gconf.set_entry("sort_order", self.set_gconf_sort_order(self.columnType.get_sort_order()))

    def sort_active(self, *args):
        """ Sort by active watches. """
        self.model.set_sort_column_id(0, not self.columnCheck.get_sort_order())
        self.specto.specto_gconf.set_entry("sort_function", "active")

    def sort_name_from_treeview_headers(self, *widget):
        """When treeview headers are clicked, GTK already does the sorting.
        Just change the active sorting radio button to 'name' in the menus, save the sorting preference."""
        self.wTree.get_widget("by_name").set_active(True)
        self.specto.specto_gconf.set_entry("sort_order", self.set_gconf_sort_order(not self.columnTitle.get_sort_order()))

    def sort_type_from_treeview_headers(self, *widget):
        """When treeview headers are clicked, GTK already does the sorting.
        Just change the active sorting radio button to 'type' in the menus, save the sorting preference."""
        self.wTree.get_widget("by_watch_type").set_active(True)
        self.sort_type()

    def sort_active_from_treeview_headers(self, *widget):
        """When treeview headers are clicked, GTK already does the sorting.
        Just change the active sorting radio button to 'active' in the menus, save the sorting preference."""
        self.wTree.get_widget("by_watch_active").set_active(True)
        self.specto.specto_gconf.set_entry("sort_order", self.set_gconf_sort_order(not self.columnCheck.get_sort_order()))

    def recreate_tray(self, *args):
        """ Recreate a tray icon if the notification area unexpectedly quits. """
        try:
            self.tray.destroy()
        except:
            pass
        self.tray = ""
        self.tray = Tray(self.specto, self)
        self.specto.watch_db.count_changed_watches()

    def show_preferences(self, *args):
        """ Show the preferences window. """
        if not self.preferences_initialized or self.preferences.get_state() == True:
            self.pref = Preferences(self.specto, self)
        else:
            self.pref.show()

    def generate_add_menu(self):
        """ Creates two "Add watch" submenus for the toplevel menu and the toolbar """
        menu_dict = self.specto.watch_db.plugin_menu
        self.add_menu = gtk.Menu()
        self.add_menu_ = gtk.Menu()

        for parent in menu_dict.keys():
            menuItem = gtk.MenuItem(parent)
            menuItem.show()

            menuItem_ = gtk.MenuItem(parent)
            menuItem_.show()

            self.add_menu.append(menuItem)
            self.add_menu_.append(menuItem_)

            childmenu = gtk.Menu()
            childmenu_ = gtk.Menu()
            for child in menu_dict[parent]:
                # Create an entry for the popup add menu
                childmenuItem = gtk.ImageMenuItem(child[0])
                childmenu.append(childmenuItem)
                img = gtk.Image()
                image = self.get_icon(child[1], 0, False)
                img.set_from_pixbuf(image)
                childmenuItem.set_image(img)
                childmenuItem.connect('button-press-event', self.show_add_watch, child[2]) #FIXME: doesn't work with the keyboard
                childmenuItem.show()

                # Create an entry for the "edit -> add" submenu
                childmenuItem_ = gtk.ImageMenuItem(child[0])
                childmenu_.append(childmenuItem_)
                img = gtk.Image()
                image = self.get_icon(child[1], 0, False)
                img.set_from_pixbuf(image)
                childmenuItem_.set_image(img)
                childmenuItem_.connect('button-press-event', self.show_add_watch, child[2])
                childmenuItem_.show()
            menuItem.set_submenu(childmenu)
            menuItem_.set_submenu(childmenu_)

        self.wTree.get_widget("button_add").set_menu(self.add_menu)
        self.wTree.get_widget("add").set_submenu(self.add_menu_)

    def position_add_watch_menu_correctly(self, *args):
        """ This is a hack, so that the popup menu appears left-aligned, right below the Add button """
        current_window_xy = self.wTree.get_widget("notifier").window.get_origin()#here's the trick to not getting screwed by the window manager. get_origin from the window property returns the root x coordinates
        current_window_x = current_window_xy[0]
        current_window_y = current_window_xy[1]
        button_x = self.wTree.get_widget("button_add").get_allocation().x
        button_y = self.wTree.get_widget("button_add").get_allocation().y
        button_height = self.wTree.get_widget("button_add").get_allocation().height
        coordinates = (current_window_x+button_x, current_window_y+button_y+button_height, False)
        return coordinates

    def show_add_watch_menu(self, *args):
        """ When the user clicks on the button part of the GTK Toolbar Menu Button, show the menu instead """
        self.add_menu.popup(None, None, self.position_add_watch_menu_correctly, 3, 0)
        return 1

    def show_add_watch(self, event, *args):
        """ Show the add watch window. """
        watch_type = args[1]
        if self.add_w == "":
            self.add_w = Add_watch(self.specto, self, watch_type)
        elif self.add_w.add_watch.flags() & gtk.MAPPED:
            pass
        else:
            self.add_w = Add_watch(self.specto, self, watch_type)

    def show_edit_watch(self, widget, *args):
        """ Show the edit watch window. """
        selected = ""
        try:
            model, iter = self.treeview.get_selection().get_selected()
            if model.iter_is_valid(iter):
                id = int(model.get_value(iter, 3))
        except:
            for watch in self.specto.watch_db:
                try:
                    if watch.name == args[0]:
                        id = watch.id
                        break
                except:
                    return

        if self.edit_w == "":
            self.edit_w = Edit_watch(self.specto, self, id)
        elif self.edit_w.edit_watch.flags() & gtk.MAPPED:
            pass
        else:
            self.edit_w = Edit_watch(self.specto, self, id)

    def show_error_log(self, *widget):
        """ Call the main function to show the log window. """
        if self.error_l == "":
            self.error_l = Log_dialog(self.specto, self)
        elif self.error_l.log_dialog.flags() & gtk.MAPPED:
            pass
        else:
            self.error_l = Log_dialog(self.specto, self)

    def show_help(self, *args):
        """ Call the main function to show the help. """
        self.specto.util.show_webpage("http://code.google.com/p/specto/w/list")

    def show_about(self, *args):
        """ Call the main function to show the about window. """
        if self.about == "":
            self.about = About(self.specto)
        elif self.about.about.flags() & gtk.MAPPED:
            pass
        else:
            self.about = About(self.specto)

    def import_watches(self, *widget):
        if self.import_watch == "":
            self.import_watch = Import_watch(self.specto, self)
        elif self.import_watch.open.open_dialog.flags() & gtk.MAPPED:
            pass
        else:
            self.import_watch = Import_watch(self.specto, self)

    def export_watches(self, *widget):
        if self.export_watch == "":
            self.export_watch = Export_watch(self.specto, self)
        elif self.export_watch.export_watch.flags() & gtk.MAPPED:
            pass
        else:
            self.export_watch = Export_watch(self.specto, self)


if __name__ == "__main__":
    #run the gui
    app = Notifier()
    gtk.main()
