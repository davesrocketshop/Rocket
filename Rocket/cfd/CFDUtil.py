# ***************************************************************************
# *   Copyright (c) 2024 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for creating a solid rocket model"""

__title__ = "FreeCAD Create Solid"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part

def getProxy(obj):
    if hasattr(obj, "Proxy"):
        return obj.Proxy
    return obj

def createSolid(obj):
    ''' Currently generates a compound object, not necessarily solid '''
    shape = None
    for current in getProxy(obj).getChildren():
        if hasattr(current, "Shape"):
            solid = getProxy(current).getSolidShape(current)
            if solid is not None and solid.isValid():
                if shape == None:
                    shape = solid
                else:
                    shape = Part.makeCompound([shape, solid])
        child = createSolid(current)
        if child is not None and child.isValid():
            if shape == None:
                shape = child
            else:
                shape = Part.makeCompound([shape, child])

    return shape

def caliber(obj):
    ''' Get the caliber of the component '''
    diameter = 0.0
    for current in getProxy(obj).getChildren():
        # print(current)
        proxy = getProxy(current)
        if hasattr(proxy, "getMaxRadius"):
            radius = FreeCAD.Units.Quantity(proxy.getMaxRadius()).Value
            diameter = max(diameter, 2.0 * radius)
        child = caliber(current)
        diameter = max(diameter, child)

    return diameter
