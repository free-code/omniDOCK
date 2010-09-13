#!/bin/bash

# This file is part of the omniDOCK project
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

# Name: setup.sh
# Purpose: Install and configure third party tools


aptitude_version="aptitude --version"
return_code=$?

if [[ $return_code == 0 ]] ; then
    use_aptitude=true
fi

if [[ $use_aptitude != true ]]; then
    yum_version="yum --version"
    return_code=$?
fi
    
