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

# Name: base.py
# Purpose: Base module to provide code that is useful to any module or child class in this app


class ConfigError(Exception):
    """
    Custom exception to denote any problem with a configuration.
    This problem can be with a config file or a misconfigured tool we depend on
    """

class DependencyError(Exception):
    """
    Custom exception for missing dependencies. We aim to use tools commonly included
    with most linux distros, but there are never guarantees in software
    """


