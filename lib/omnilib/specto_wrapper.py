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

from subprocess import Popen
from spectlib import util

class SpectoWrapper:
    """
    Reuses code from the specto project
    """
    

    def __init__(self):
        """
        Start specto in console mode, and set any useful instance variables

        >>> test = SpectoWrapper()

        >>> type(test.running_process)
        <class 'subprocess.Popen'>

        >>> type(test.pid)
        <type 'int'>

        >>> type(test.config_dir)
        <type 'str'>

        >>> "specto" in test.config_dir
        True
        """
        try:
            self.running_process = Popen(["specto", "--console"])
        except:
            self.running_process = Popen(["./specto.py", "--console"])
        finally:
            self.pid = self.running_process.pid

        self.config_dir = util.get_path("specto")


    def __del__(self):
        """
        Clean up before we go
        """
        self.running_process.kill()


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


def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()
