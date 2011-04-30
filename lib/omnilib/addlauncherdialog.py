import gtk

class AddLauncherDialog(gtk.Window):
    def __init__(self, add_launcher_cb):
        self.add_launcher_cb = add_launcher_cb
        super(gtk.Window, self).__init__()
        self.set_title("Add a Launcher")
        self.set_size_request(400,200)
        self.result = {}
        self.set_modal(True)
        self._make_gui()
        self.show_all()


    def _make_gui(self):
        table = gtk.Table(8, 8, homogeneous=True)
        okButton = gtk.Button("OK")
        okButton.connect("clicked", self._ok_clicked)
        cancelButton = gtk.Button("Cancel")
        cancelButton.connect("clicked", self._cancel_clicked)

        nameLabel = gtk.Label("Name:")
        self.nameEntry = gtk.Entry()
        
        iconLabel = gtk.Label("Icon:")
        self.iconEntry = gtk.Entry()
        iconBrowseButton = gtk.Button("Browse")
        iconBrowseButton.connect("clicked", self._browse_for_file)

        execLabel = gtk.Label("Command:")
        self.execEntry = gtk.Entry()


        table.attach(nameLabel,0,2,1,2)
        table.attach(self.nameEntry, 2,6,1,2)
        table.attach(iconLabel, 0,2,2,3)
        table.attach(self.iconEntry,2,6,2,3)
        table.attach(iconBrowseButton,6,8,2,3)
        table.attach(execLabel,0,2,3,4)
        table.attach(self.execEntry,2,6,3,4)
        table.attach(cancelButton, 0,3,7,8)
        table.attach(okButton,5,8,7,8)
        self.add(table)


    def _ok_clicked(self, data):
        self.result["name"] = self.nameEntry.get_text()
        self.result["icon"] = self.iconEntry.get_text()
        self.result["exec"] = self.execEntry.get_text()
        self.result["auto"] = "true"
        self.add_launcher_cb(self.result, isnew=True)
        self.destroy()


    def _cancel_clicked(self, data):
        print "cancel clicked"
        self.destroy()
        return False


    def _browse_for_file(self, data):
        iconDialog = gtk.FileChooserDialog(title="Select Icon",
                                                 parent=self,
                                                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                                 buttons=(gtk.STOCK_CANCEL,
                                                         gtk.RESPONSE_CANCEL,
                                                         gtk.STOCK_OPEN,
                                                         gtk.RESPONSE_OK),
                                                backend=None)
        iconDialog.set_default_response(gtk.RESPONSE_OK)
        response=iconDialog.run()
        if response == gtk.RESPONSE_OK:
            iconPath = iconDialog.get_filename()
            self.iconEntry.set_text(iconPath)
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        iconDialog.destroy()