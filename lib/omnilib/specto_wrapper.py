# This file is part of the uberdock project
# See the AUTHORS file for copyright ownership information
#
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

# Name: specto_wrapper.py
# Purpose: Instantiate and use classes from specto

import sys; sys.path += ['lib/']
from subprocess import Popen
from spectlib import util

class SpectoWrapper:
    """
    Reuses code from the specto project
    """

    def __init__(self, gui_callback=None):
        """
        Set any useful instance variables

        >>> test = SpectoWrapper()

        >>> type(test.config_dir)
        <type 'str'>

        >>> "specto" in test.config_dir
        True
        """
        self.config_dir = util.get_path("specto")
        self.gui_callback = gui_callback

    def start_daemon(self):
        """
        Start the specto daemon

        >>> test = SpectoWrapper()

        >>> test.start_daemon()

        >>> type(test.specto_process)
        <class 'subprocess.Popen'>

        >>> type(test.specto_pid)
        <type 'int'>
        """
        try:
            self.specto_process = Popen(["specto", "--console"])
        except:
            self.specto_process = Popen(["./lib/specto", "--console"])
        finally:
            self.specto_pid = self.specto_process.pid


    def watches(self):
        """
        Return a dictionary of watches

        >>> test = SpectoWrapper()

        >>> type(test.watches())
        <type 'dict'>
        """
        watches_list = self.config_dir + "/watches.list"
        watch_dictionary = {}
        input = open(watches_list, 'r')
        
        for line in input:
            line = line.strip('\n')
            
            if '[' and ']' in line:
                line = line[1:-1]
                watch_dictionary[line] = {}
                key = line
                
            elif '=' in line:
                line = line.split('=')
                sub_key = line[0].strip()
                value = line[1].strip()
                watch_dictionary[key][sub_key] = value

            elif line == '':
                pass

        return watch_dictionary


    def start_watching_the_watchlist(self, interval_in_minutes=5):
        """
        Watch the results of specto and update the gui
        Just a stub right now until I can figure out a good time based
        solution without causing the gui app to hang.
        """
        


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
