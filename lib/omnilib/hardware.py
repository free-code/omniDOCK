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

# Name: hardware.py
# Purpose: Provide an api to return hardware sensor related values such as
#          temperature, fan speed, etc


try:
    from omnilib.base import *
except ImportError:
    ConfigError = Exception
    DependencyError = Exception
finally:
    import commands


class Hardware:
    """
    Provide an api to return hardware sensor related values such as
    temperature, fan speed, etc
    """


    def __init__(self):
        """
        Quick test to ensure lm-sensors is installed and configured correctly
        """
        sensor_config_test = commands.getoutput("sensors")
        if "No sensors found" in sensor_config_test:
            raise ConfigError("Sensors not configured. Try running sudo sensors-detect")
        elif "command not found" in sensor_config_test:
            raise DependencyError("lm-sensor package not installed, or no found in $PATH")


    def poll_sensors(self):
        """
        Poll all the hardware sensors.

        >>> test = Hardware()

        >>> test.poll_sensors().keys()
        ['fan', 'cpu', 'temp']

        >>> for key in test.poll_sensors().keys():
        ...     type(test.poll_sensors()[key])
        ... 
        <type 'dict'>
        <type 'dict'>
        <type 'dict'>
        """
        values = {'cpu':{}, 'fan':{}, 'temp':{}}
        input = commands.getoutput("sensors -f")
        input = input.split("\n")

        for line in input:
            if "Core" in line or "Temp" in line or "Fan" in line:
                line = line.split()
                sensor = line[0] + " " + line[1].strip(':') #Example: "Core 0"
                measurement = line[2]

                if "Core" in sensor:
                    values['cpu'][sensor] = measurement
                elif "Temp" in sensor:
                    values['temp'][sensor] = measurement
                elif "Fan" in sensor:
                    values['fan'][sensor] = measurement

        return values





def _test():
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()


