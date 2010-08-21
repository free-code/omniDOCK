#!/usr/bin/env python
#this script is for translators.
#It is used to regenerate the translations template file (po/specto.pot)
#when strings in specto have changed.

print "Specto's custom string extractor script\n"

import os
import glob
from string import replace
paths = ["../spectlib", "../spectlib/tools",
         "../spectlib/plugins", "../data/glade"]
extensions = [".py", ".h"]
arguments = ""

#this is to extract the strings from the glade files
#before passing them to pygettext
#intltool-extract --type=gettext/glade pywine.glade
print "Parsing glade files..."
for x in glob.glob("../data/glade/*.glade"):
    glade_file_to_parse = "intltool-extract --type=gettext/glade " + x
    os.system(glade_file_to_parse)
print "\tDone.\n"

#use pygettext to transform strings in the .glade.h files
#and strings in .py files into a specto.pot template file
for path in paths:
    for extension in extensions:
        foo = path + "/*" + extension
        for x in glob.glob(foo):
            arguments += x
            arguments += " "
# Here is a hack to prevent indexing that file:
arguments = replace(arguments, " ../spectlib/i18n.py", "")
print "Will analyze these files:\n\n", arguments

command = "pygettext --keyword=N_ --output=specto.pot " + arguments
os.system(command)
print "\n\nSTRINGS EXTRACTED. They have been saved" \
        " as the template file 'specto.pot'"
