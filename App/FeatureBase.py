# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for Python Features"""

__title__ = "FreeCAD Rocket Features"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod

from App.Constants import FEATURE_VERSION

class FeatureBase:

    def __init__(self, obj):
        super().__init__()
       
        self.Type = self.featureType()
        self._obj = obj
        obj.Proxy=self
        self.version = FEATURE_VERSION
        
        self._initAttributes(obj)
        self._initVars(obj)

    def onDocumentRestored(self, obj):
        obj.Proxy=self
        
        # Add any missing attributes
        self._initAttributes(obj)
        self._initVars(obj)

        self._obj = obj

    @abstractmethod
    def _initAttributes(self, obj):
        pass

    @abstractmethod
    def _initVars(self, obj):
        pass

    @abstractmethod
    def featureType(self):
        """ Returns the string representing the feature type """

    def __getstate__(self):
        return self.version

    def __setstate__(self, state):
        if state:
            self.version = state
