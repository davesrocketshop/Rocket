# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
"""Base class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Utilities import _err

from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, LOCATION_BASE

def QT_TRANSLATE_NOOP(scope, text):
    return text

class ShapeComponent:

    def __init__(self, obj):
        if not hasattr(obj, 'Manufacturer'):
            obj.addProperty('App::PropertyString', 'Manufacturer', 'RocketComponent', QT_TRANSLATE_NOOP('App::Property', 'Component manufacturer')).Manufacturer = ""
        if not hasattr(obj, 'PartNumber'):
            obj.addProperty('App::PropertyString', 'PartNumber', 'RocketComponent', QT_TRANSLATE_NOOP('App::Property', 'Component manufacturer part number')).PartNumber = ""
        if not hasattr(obj, 'Description'):
            obj.addProperty('App::PropertyString', 'Description', 'RocketComponent', QT_TRANSLATE_NOOP('App::Property', 'Component description')).Description = ""
        if not hasattr(obj, 'Material'):
            obj.addProperty('App::PropertyString', 'Material', 'RocketComponent', QT_TRANSLATE_NOOP('App::Property', 'Component material')).Material = ""

        obj.Proxy=self
        self.version = '3.0'
        self._scratch = {} # None persistent property storage, for import properties and similar

    def __getstate__(self):
        return self.version

    def __setstate__(self, state):
        if state:
            self.version = state

    def setScratch(self, name, value):
        self._scratch[name] = value

    def getScratch(self, name):
        return self._scratch[name]

    def isScratch(self, name):
        return name in self._scratch

    # This will be implemented in the derived class
    def execute(self, obj):
        _err("No execute method defined for %s" % (self.__class__.__name__))

class ShapeLocation(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)
        
        if not hasattr(obj, 'LocationReference'):
            obj.addProperty('App::PropertyEnumeration', 'LocationReference', 'RocketComponent', QT_TRANSLATE_NOOP('App::Property', 'Reference location for the location'))
        obj.LocationReference = [
                    LOCATION_PARENT_TOP,
                    LOCATION_PARENT_MIDDLE,
                    LOCATION_PARENT_BOTTOM,
                    LOCATION_BASE
                ]
        obj.LocationReference = LOCATION_PARENT_BOTTOM
        if not hasattr(obj, 'Location'):
            obj.addProperty('App::PropertyDistance', 'Location', 'RocketComponent', QT_TRANSLATE_NOOP('App::Property', 'Location offset from the reference')).Location = 0.0
        if not hasattr(obj, 'RadialOffset'):
            obj.addProperty('App::PropertyAngle', 'RadialOffset', 'RocketComponent', QT_TRANSLATE_NOOP('App::Property', 'Radial offset from the vertical')).RadialOffset = 0.0
