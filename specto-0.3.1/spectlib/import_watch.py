# -*- coding: UTF8 -*-

# Specto , Unobtrusive event notifier
#
#       import_export.py
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
from spectlib.i18n import _
import os
from spectlib.watch import Watch_io
from spectlib.watch import Watch_collection

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

try:
    import gtk
    import gtk.glade
    import gobject
except:
    pass


class Import_watch:
    """
    Class to create the import/export watch dialog.
    """

    def __init__(self, specto, notifier):
        self.specto = specto
        self.notifier = notifier

        self.open = Open_dialog(self.specto, self, None)

    def create_import_window(self):
        #create tree
        gladefile = os.path.join(self.specto.PATH, "glade/import_export.glade")
        windowname = "import_export"
        self.wTree = gtk.glade.XML(gladefile, windowname, self.specto.glade_gettext)
        self.import_watch = self.wTree.get_widget("import_export")

        self.import_watch.set_title(_("Import watches"))
        self.wTree.get_widget("button_action").set_label(_("Import watches"))

        self.model = gtk.ListStore(gobject.TYPE_BOOLEAN, gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING)
        self.new_watch_db = {}

        #catch some events
        dic = {"on_button_select_all_clicked": self.select_all,
            "on_button_deselect_all_clicked": self.deselect_all,
            "on_button_action_clicked": self.import_watches,
            "on_button_close_clicked": self.delete_event}

        #attach the events
        self.wTree.signal_autoconnect(dic)

        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.import_watch.set_icon(icon)

        self.treeview = self.wTree.get_widget("treeview")
        self.treeview.set_model(self.model)
        self.treeview.set_flags(gtk.TREE_MODEL_ITERS_PERSIST)
        self.iter = {}

        ### Checkbox
        self.renderer = gtk.CellRendererToggle()
        self.renderer.set_property("activatable", True)
        self.renderer.connect("toggled", self.check_clicked, self.model)
        self.columnCheck = gtk.TreeViewColumn(_("Select"), self.renderer, active=0)
        self.treeview.append_column(self.columnCheck)

        ### Icon
        self.renderer = gtk.CellRendererPixbuf()
        self.columnIcon = gtk.TreeViewColumn(_("Type"), self.renderer, pixbuf=1)
        self.treeview.append_column(self.columnIcon)

        ### Titre
        self.renderer = gtk.CellRendererText()
        self.columnTitel = gtk.TreeViewColumn(_("Name"), self.renderer, markup=2)
        self.columnTitel.set_expand(True)
        self.columnTitel.set_resizable(True)
        self.treeview.append_column(self.columnTitel)

        ### ID
        self.renderer = gtk.CellRendererText()
        self.column = gtk.TreeViewColumn(_("ID"), self.renderer, markup=3)
        self.column.set_visible(False)
        #self.column.set_sort_column_id(3)
        self.treeview.append_column(self.column)

        ### type
        self.renderer = gtk.CellRendererText()
        self.columnType = gtk.TreeViewColumn(_("TYPE"), self.renderer, markup=4)
        self.columnType.set_visible(False)
        #self.columnType.set_sort_column_id(4)
        self.treeview.append_column(self.columnType)

    def select_all(self, widget):
        db = self.new_watch_db
        for watch in db:
            if watch.deleted == False:
                self.model.set_value(self.iter[watch.id], 0, 1)

    def deselect_all(self, widget):
        db = self.new_watch_db
        for watch in db:
            if watch.deleted == False:
                self.model.set_value(self.iter[watch.id], 0, 0)

    def import_watches(self, widget):
        self.import_watch.hide_all()

        watches = self.get_selected_watches()
        all_values = {}
        for i in watches:
            values = {}
            watch = self.new_watch_db[watches[i].id]
            values.update(self.new_watch_db[watches[i].id].get_values())

            values['name'] = watch.name
            if self.specto.watch_io.is_unique_watch(values['name']):
                y = 1
                while self.specto.watch_io.is_unique_watch(values['name'] + str(y)):
                    y += 1
                values['name'] = values['name'] + str(y)

            values['type'] = watch.type
            values['refresh'] = watch.refresh
            values['active'] = True
            values['last_changed'] = watch.last_changed
            values['changed'] = False
            all_values[i] = values
        _id = self.specto.watch_db.create(all_values)

        for values in all_values.values():
            self.specto.watch_io.write_watch(values)

        for id in _id:  # Create notifier entries
            self.specto.notifier.add_notifier_entry(id)

        for id in _id:  # Start the new watches
            self.specto.watch_db[id].start()

    def delete_event(self, widget, *args):
        """ Destroy the window. """
        self.import_watch.destroy()
        return True

    def get_selected_watches(self):
        selected_watches_db = {}
        i = 0
        watch_db = self.new_watch_db
        for watch in watch_db:
            if watch.deleted == False:
                if self.model.get_value(self.iter[watch.id], 0) == True:
                    selected_watches_db[i] = watch
                    i += 1
        return selected_watches_db

    def add_watch_entry(self, id):
        """ Add an entry to the notifier list. """
        watch = self.new_watch_db[id]
        entry_name = watch.name.replace("&", "&amp;")
        icon = self.notifier.get_icon(watch.icon, 50, False)
        self.iter[id] = self.model.insert_before(None, None)
        self.model.set_value(self.iter[id], 0, 0)
        self.model.set_value(self.iter[id], 1, icon)#self.specto.notifier.make_transparent(icon, 50))#does not need transparency here
        self.model.set_value(self.iter[id], 2, entry_name)
        self.model.set_value(self.iter[id], 3, watch.id)
        self.model.set_value(self.iter[id], 4, watch.type)

    def set_new_watch_db(self, watch_db):
        self.new_watch_db = watch_db

    def check_clicked(self, object, path, model):
        """ Call the main function to start/stop the selected watch. """
        sel = self.treeview.get_selection()
        sel.select_path(path)
        model, iter = self.treeview.get_selection().get_selected()

        if model.get_value(iter, 0):
            model.set_value(iter, 0, 0)
        else:
            model.set_value(iter, 0, 1)


class Open_dialog:
    """
    Class for displaying the open dialog.
    """

    def __init__(self, specto, _import, watches_db):
        self.specto = specto
        self._import = _import
        # Create the tree
        gladefile = os.path.join(self.specto.PATH, "glade/import_export.glade")
        windowname = "filechooser"
        self.wTree = gtk.glade.XML(gladefile, windowname)
        self.open_dialog = self.wTree.get_widget("filechooser")

        dic = {"on_button_cancel_clicked": self.cancel,
            "on_button_save_clicked": self.open}
        # Attach the events
        self.wTree.signal_autoconnect(dic)

        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.open_dialog.set_icon(icon)
        self.open_dialog.set_filename(os.environ['HOME'] + "/ ")

    def cancel(self, *args):
        """ Close the save as dialog. """
        self.open_dialog.destroy()

    def open(self, *args):
        """ Save the file. """
        self.open_dialog.hide_all()
        self._import.create_import_window()
        file_name = self.open_dialog.get_filename()
        self.read_options(file_name)
        self._import.import_watch.show()
        self.open_dialog.destroy()

    def read_options(self, file_name):
        watch_io = Watch_io(self.specto, file_name)
        if watch_io.valid == False:
            return False

        values = watch_io.read_all_watches()
        for i in values:
            try:
                int(values[i]['type'])
            except:
                pass
            else:
                values[i]['open_command'] = ""
                values[i]['last_changed'] = ""

            # Import from Specto 0.2
            # FIXME: wouldn't this code be more efficient with a case/switch?
            if values[i]['type'] == "0":
                values[i]['type'] = "Watch_web_static"
            elif values[i]['type'] == "1":
                if values[i]['prot'] == "0":
                    values[i]['type'] = "Watch_mail_pop3"
                if values[i]['prot'] == "1":
                    values[i]['type'] = "Watch_mail_imap"
                if values[i]['prot'] == "2":
                    values[i]['type'] = "Watch_mail_gmail"
                del values[i]['prot']
            elif values[i]['type'] == "2":
                if values[i]['mode'] == "file":
                    values[i]['type'] = "Watch_system_file"
                else:
                    values[i]['type'] = "Watch_system_folder"
                del values[i]['mode']
            elif values[i]['type'] == "3":
                values[i]['type'] = "Watch_system_process"
            elif values[i]['type'] == "4":
                values[i]['type'] = "Watch_system_port"
            elif values[i]['type'] == "5":
                values[i]['type'] = "Watch_web_greader"
        watch_collection = Watch_collection(self.specto)
        watch_collection.create(values)
        self._import.set_new_watch_db(watch_collection)
        for watch in watch_collection:
            self._import.add_watch_entry(watch.id)


if __name__ == "__main__":
    # Run the gui
    app = Import_watch()
    gtk.main()
