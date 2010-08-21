#!/usr/bin/env python
import os
from distutils.core import setup

f=open('data/doc/VERSION', 'r')  # Open the VERSION file for reading.
# Below, "[:-1]" means we omit the last character, which is "\n".
version_string = f.readline()[:-1]
f.close


def give_files(dir, *extension):
    files=[]
    all_files=os.listdir(dir)
    for file in all_files:
        ext=(os.path.splitext(file))[1]
        if ext in extension:
            files.append(dir + file)
    return files


# List all the languages, separated by one whitespace
i18n_languages = "fr cs de es it pt_BR ro ru sv tr zh_CN"


def give_mo_file(lang):
    return "po/" + str(lang) + "/specto.mo"


def give_mo_path(lang):
    return "share/locale/" + str(lang) + "/LC_MESSAGES/"


def give_mo_tuples(langs):
    mo_tuple_list=[]
    for lang in langs.split(' '):
        mo_tuple_list.append((give_mo_path(lang), [give_mo_file(lang)]))
    return mo_tuple_list


temp_files = [
    # The paths are relative to sys.prefix
    ('share/doc/specto', give_files('data/doc/', '')),
    ('share/icons/hicolor/scalable/apps', ['data/icons/hicolor/scalable/specto.svg']),
    ('share/applications', ['specto.desktop']),
    ('share/specto/icons', give_files('data/icons/', '.png', '.svg')),
    ('share/specto/glade', give_files('data/glade/', '.glade'))]

for lang_tuple in give_mo_tuples(i18n_languages):
    temp_files.append(lang_tuple)

setup(name = "specto",
    version = version_string,
    description = "A desktop application that will watch configurable events (website updates, emails, file and folder changes...)",
    author = "Jean-Francois Fortin Tam",
    author_email = "nekohayo at gmail dot com",
    url = "http://specto.sourceforge.net",
    packages = [('spectlib'), ('spectlib/plugins'), ('spectlib/tools')],
    #package_dir = {'': 'src'},
    #package_data = {'specto': ['preferences.glade', 'notify.glade']},
    scripts = ['specto'],
    data_files = temp_files)
