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

# Name: system.py
# Purpose: Provide an api to return system related values such as
#           CPU, RAM, and filesystem usage.

import commands

class System:
    """
    Class to provide system related values such as
    CPU, RAM, and filesystem usage.
    """


    def cpu_usage(self):
        """
        Return an integer that represents percentage of cpu used

        >>> test = System()

        >>> type(test.cpu_usage())
        <type 'int'>

        >>> test.memory_usage() > -1
        True

        >>> test.memory_usage() < 101
        True
        """
        input = commands.getoutput("ps -Ao %cpu")
        input = input.split("\n")
        del input[0]
        usage_percentage = 0.0 

        for process in input:
            usage_percentage += float(process)

        return int(usage_percentage)


    def memory_usage(self):
        """
        Return an integer that represents percentage of RAM used

        >>> test = System()

        >>> type(test.memory_usage())
        <type 'int'>

        >>> test.memory_usage() > -1
        True

        >>> test.memory_usage() < 101
        True
        """
        usage = 0
        temp = {}
        input = commands.getoutput("free -m")
        ram_line = input.split('\n')[1]
        ram_line = ram_line.split()
        ram_line = ram_line[1:-1]
        
        index = 0
        for value in ram_line:
            ram_line[index] = float(value)
            index += 1

        temp['total'] = ram_line[0]
        temp['used'] = ram_line[1]
        usage = (temp['used'] / temp['total']) * 100.0
        return int(usage)


    def filesystem_usage(self):
        """
        Return a dictionary of partition names and space usage

        >>> test = System()

        >>> type(test.filesystem_usage())
        <type 'dict'>

        >>> test.filesystem_usage().keys().count("/")
        1
        """
        usage = {}
        input = commands.getoutput("df -h")
        input = input.split("\n")
        del input[0]

        for line in input:
            if "/" and "%" in line:
                line = line.split()
                partition = line[-1]
                usage[partition] = {'percentage':line[-2],
                                    'available':line[-3],
                                    'used':line[-4],
                                    'size':line[-5]}

        return usage



def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()


