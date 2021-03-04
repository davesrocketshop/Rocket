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
"""Component class for rocket nose cones"""

__title__ = "FreeCAD Open Rocket Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD as App

from App.Component.Component import Component

class RocketComponent(Component):

    def __init__(self, doc):
        super().__init__(doc)

        self._designer = ""
        self._version = None

    def create(self, parent=None):
        #obj = self._doc.addObject('Part::FeaturePython', self._name)
        obj = App.ActiveDocument.addObject("App::DocumentObjectGroupPython", self._name)
        super().create(obj)

