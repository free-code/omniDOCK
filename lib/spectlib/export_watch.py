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


class Export_watch:
    """
    Class to create the import/export watch dialog.
    """

    def __init__(self, specto, notifier):
        self.specto = specto
        self.notifier = notifier

        #create tree
        gladefile = os.path.join(self.specto.PATH, "glade/import_export.glade")
        windowname = "import_export"
        self.wTree = gtk.glade.XML(gladefile, windowname, \
                                   self.specto.glade_gettext)
        self.export_watch = self.wTree.get_widget("import_export")
        self.export_watch.set_title(_("Export watches"))
        self.wTree.get_widget("button_action").set_label(_("Export watches"))

        self.model = gtk.ListStore(gobject.TYPE_BOOLEAN, gtk.gdk.Pixbuf, \
                    gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING)
        self.new_watch_db = {}

        #catch some events
        dic = {"on_button_select_all_clicked": self.select_all,
              "on_button_deselect_all_clicked": self.deselect_all,
              "on_button_action_clicked": self.do_action,
              "on_button_close_clicked": self.delete_event}

        #attach the events
        self.wTree.signal_autoconnect(dic)

        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.export_watch.set_icon(icon)

        self.treeview = self.wTree.get_widget("treeview")
        self.treeview.set_model(self.model)
        self.treeview.set_flags(gtk.TREE_MODEL_ITERS_PERSIST)
        self.iter = {}

        ### Checkbox
        self.renderer = gtk.CellRendererToggle()
        self.renderer.set_property("activatable", True)
        self.renderer.connect("toggled", self.check_clicked, self.model)
        self.columnCheck = gtk.TreeViewColumn(_("Select"), \
                            self.renderer, active=0)
        self.treeview.append_column(self.columnCheck)

        ### Icon
        self.renderer = gtk.CellRendererPixbuf()
        self.columnIcon = gtk.TreeViewColumn(_("Type"), \
                            self.renderer, pixbuf=1)
        self.treeview.append_column(self.columnIcon)

        ### Titre
        self.renderer = gtk.CellRendererText()
        self.columnTitel = gtk.TreeViewColumn(_("Name"), \
                            self.renderer, markup=2)
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
        self.columnType = gtk.TreeViewColumn(_("TYPE"), \
                            self.renderer, markup=4)
        self.columnType.set_visible(False)
        #self.columnType.set_sort_column_id(4)
        self.treeview.append_column(self.columnType)

        for watch in self.specto.watch_db:
            if watch.deleted == False:
                self.add_watch_entry(watch.id)

    def select_all(self, widget):
        db = self.specto.watch_db

        for watch in db:
            if watch.deleted == False:
                self.model.set_value(self.iter[watch.id], 0, 1)

    def deselect_all(self, widget):
        db = self.specto.watch_db

        for watch in db:
            if watch.deleted == False:
                self.model.set_value(self.iter[watch.id], 0, 0)

    def do_action(self, widget):
        self.export_watch.hide_all()
        self.save = Save_dialog(self.specto, None, False, \
                            self.get_selected_watches())

    def delete_event(self, widget, *args):
        """ Destroy the window. """
        self.export_watch.destroy()
        return True

    def get_selected_watches(self):
        selected_watches_db = {}
        i = 0
        watch_db = self.specto.watch_db

        for watch in watch_db:
            if watch.deleted == False:
                if self.model.get_value(self.iter[watch.id], 0) == True:
                    selected_watches_db[i] = watch
                    i += 1
        return selected_watches_db

    def add_watch_entry(self, id):
        """ Add an entry to the notifier list. """
        watch = self.specto.watch_db[id]
        entry_name = watch.name.replace("&", "&amp;")
        icon = self.notifier.get_icon(watch.icon, 50, False)
        self.iter[id] = self.model.insert_before(None, None)
        self.model.set_value(self.iter[id], 0, 0)
        self.model.set_value(self.iter[id], 1, icon)
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


class Save_dialog:
    """
    Class for displaying the save as dialog.
    """

    def __init__(self, specto, _import, action_type, watches_db):
        self.specto = specto
        self._export = _import
        #create tree
        gladefile = os.path.join(self.specto.PATH, "glade/import_export.glade")
        windowname = "filechooser"
        self.wTree = gtk.glade.XML(gladefile, windowname)
        self.save_dialog = self.wTree.get_widget("filechooser")
        self.action_type = action_type

        self.save_dialog.set_action(gtk.FILE_CHOOSER_ACTION_SAVE)
        self.wTree.get_widget("button_save").set_label("gtk-save")
        self.watches_db = watches_db

        dic = {"on_button_cancel_clicked": self.cancel,
             "on_button_save_clicked": self.save}
        #attach the events
        self.wTree.signal_autoconnect(dic)

        icon = gtk.gdk.pixbuf_new_from_file(os.path.join(self.specto.PATH, "icons/specto_window_icon.png"))
        self.save_dialog.set_icon(icon)
        self.save_dialog.set_filename(os.environ['HOME'] + "/ ")

    def cancel(self, *args):
        """ Close the save as dialog. """
        self.save_dialog.destroy()

    def save(self, *args):
        """ Save the file. """
        file_name = self.save_dialog.get_filename()

        for i in self.watches_db.keys():
            values = {}
            values['name'] = self.watches_db[i].name
            values['type'] = self.watches_db[i].type
            values['refresh'] = self.watches_db[i].refresh
            values.update(self.watches_db[i].get_values())
            self.write_options(file_name, values)

        self.save_dialog.destroy()

    def write_options(self, file_name, values):
        """
        Write or change the watch options in a configuration file.
        Values has to be a dictionary with the name from the options
        and the value. example: { 'name':'value', 'name':'value' }
        If the name is not found, a new watch will be added,
        else the excisting watch will be changed.
        """
        watch_io = Watch_io(self.specto, file_name)
        watch_io.write_watch(values)

if __name__ == "__main__":
    #run the gui
    app = Export_watch()
    gtk.main()
