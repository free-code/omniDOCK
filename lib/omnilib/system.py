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
        Return a dictionary of aggregated cpu usage
        """
        temp = {}
        usage = {}
        input = commands.getoutput("head -1 /proc/stat")
        cpu_line = input.split()[1:-1] #Get rid of "cpu"
        
        #Convert all the values from string to numeric
        index = 0
        for hertz in cpu_line:
            cpu_line[index] = int(hertz)
            index += 1 

        #Parse out the values we need        
        temp['user'] = cpu_line[0]
        temp['nice'] = cpu_line[1]
        temp['system'] = cpu_line[2]
        temp['idle'] = cpu_line[3]
        temp['io_wait'] = cpu_line[4]
        temp['irq'] = cpu_line[5]
        temp['soft_irq'] = cpu_line[6]
        temp['total'] = 0.0
        for hertz in cpu_line:
            temp['total'] += hertz
        
        #Convert to percentages
        for key in temp.keys():
            usage[key] = (temp[key] / temp['total']) * 100
            usage[key] = int(usage[key])
        
        return usage


    def memory_usage(self):
        """
        Return a dictionary of memory usage as percentages
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

