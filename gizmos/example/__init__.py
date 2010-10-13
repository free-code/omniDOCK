# -*- coding: utf-8 -*-
#!/usr/bin/env python
class TerminalGizmo: 
    def make_term(self):
	try:
	    import gtk
	except:
	    print >> sys.stderr, "You need to install the python gtk bindings"
	    sys.exit(1)
	
	# import vte
	try:
	    import vte
	except:
	    error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
	    'You need to install python bindings for libvte')
	    error.run()
	    sys.exit (1)
	

	v = vte.Terminal ()
	v.connect ("child-exited", lambda term: gtk.main_quit())
	v.fork_command()
	window = gtk.ScrolledWindow()
	window.add(v)
	#window.connect('delete-event', lambda window, event: gtk.main_quit())
	window.show_all()
	#gtk.main()
        return window

def get_gizmo():
    term = TerminalGizmo()
    return (term.make_term(), (3,3), "omniDOCK Terminal")








print "EXAMPLE loaded"