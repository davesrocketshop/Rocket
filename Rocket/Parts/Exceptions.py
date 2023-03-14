# ***************************************************************************
# *   Copyright (c) 2021-2023 David Carter <dcarter@davidcarter.ca>         *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Class for part import exceptions"""

__title__ = "FreeCAD Rocket Import Exceptions"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

class InvalidError(Exception):

    def __init__(self, manufacturer, partNo, message):
        self._manufacturer = manufacturer
        self._name = partNo
        self._message = message

class MultipleEntryError(Exception):

    def __init__(self, message="Multiple entries found"):
        self._message = message    

class UnknownManufacturerError(Exception):

    def __init__(self, message="Unknown manufacturer"):
        self._message = message

class MaterialNotFoundError(Exception):

    def __init__(self, message="Unknown material"):
        self._message = message

class NotFoundError(Exception):

    def __init__(self, message="Unknown material"):
        self._message = message
