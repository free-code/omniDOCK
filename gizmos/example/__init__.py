# -*- coding: utf-8 -*-

def get_gizmo():
    """This is the only method necessary to make a gizmo.
       It should return a gtk widget, size tuple, and name.  
       Anything else is up to you"""
    term = TerminalGizmo()
    return (term.make_term(), (3,3), "omniDOCK Terminal")

print "EXAMPLE loaded"

# # # # # # # # # An example Gizmo

class TerminalGizmo: 
    def make_term(self):
	try:
	    import gtk
	except:
	    print >> sys.stderr, "You need to install the python gtk bindings"
	    sys.exit(1)
	
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
	window.show_all()
        return window