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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from PySide import QtGui, QtCore
import FreeCAD
import FreeCADGui
import Part

from App.OpenRocket import _msg, _err, _trace
from App.ConeShapeHandler import ConeShapeHandler
from App.EllipseShapeHandler import EllipseShapeHandler
from App.HaackShapeHandler import HaackShapeHandler
from App.OgiveShapeHandler import OgiveShapeHandler
from App.ParabolicShapeHandler import ParabolicShapeHandler
from App.PowerShapeHandler import PowerShapeHandler

from App.NoseShapeHandler import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.NoseShapeHandler import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID

class ViewProviderNoseCone:

	def __init__(self, viewObject):
		obj.Proxy = self

	def getDefaultDisplayMode(self):
		return "Flat Lines"

	def onChanged(self, vp, prop):
		FreeCAD.Console.PrintMessage('Change property: ' + str(prop) + '\n')

class NoseCone:

	def __init__(self, obj, noseType, noseStyle,
			length, radius, thickness, coefficient, resolution,
			shoulder, shoulderLength, shoulderRadius, shoulderThickness):
		_trace(self.__class__.__name__, "__init__")

		obj.addProperty('App::PropertyLength', 'Length', 'NoseCone', 'Length of the nose not including any shoulder').Length = length
		obj.addProperty('App::PropertyLength', 'Radius', 'NoseCone', 'Radius at the base of the nose').Radius = radius
		obj.addProperty('App::PropertyLength', 'Thickness', 'NoseCone', 'Nose cone thickness').Thickness = thickness
		obj.addProperty('App::PropertyBool', 'Shoulder', 'NoseCone', 'Set to true if the part includes a shoulder').Shoulder = shoulder
		obj.addProperty('App::PropertyLength', 'ShoulderLength', 'NoseCone', 'Shoulder Length').ShoulderLength = shoulderLength
		obj.addProperty('App::PropertyLength', 'ShoulderRadius', 'NoseCone', 'Shoulder radius').ShoulderRadius = shoulderRadius
		obj.addProperty('App::PropertyLength', 'ShoulderThickness', 'NoseCone', 'Shoulder thickness').ShoulderThickness = shoulderThickness
		obj.addProperty('App::PropertyFloat', 'Coefficient', 'NoseCone', 'Coefficient').Coefficient = coefficient
		obj.addProperty('App::PropertyInteger', 'Resolution', 'NoseCone', 'Resolution').Resolution = resolution

		obj.addProperty('App::PropertyEnumeration', 'NoseType', 'NoseCone', 'Nose cone type')
		obj.NoseType = [TYPE_CONE,
					TYPE_ELLIPTICAL,
					TYPE_OGIVE,
					TYPE_VON_KARMAN,
					TYPE_PARABOLA,
					TYPE_PARABOLIC,
					TYPE_POWER,
					TYPE_HAACK]
		obj.NoseType = noseType

		obj.addProperty('App::PropertyEnumeration', 'NoseStyle', 'NoseCone', 'Nose cone style')
		obj.NoseStyle = [STYLE_SOLID,
							STYLE_HOLLOW,
							STYLE_CAPPED]
		obj.NoseStyle = noseStyle

		obj.addProperty('Part::PropertyPartShape', 'Shape', 'NoseCone', 'Shape of the nose cone')
		#obj.Proxy=self


	def execute(self, obj):
		_trace(self.__class__.__name__, "draw")

		shape = None
		if obj.NoseType == TYPE_CONE:
			shape = ConeShapeHandler(obj)
		elif obj.NoseType == TYPE_ELLIPTICAL:
			shape = EllipseShapeHandler(obj)
		elif obj.NoseType == TYPE_OGIVE:
			shape = OgiveShapeHandler(obj)
		elif obj.NoseType == TYPE_VON_KARMAN:
			self._obj.Coefficient = 0.0
			shape = HaackShapeHandler(obj)
		elif obj.NoseType == TYPE_HAACK:
			shape = HaackShapeHandler(obj)
		elif obj.NoseType == TYPE_PARABOLIC:
			shape = ParabolicShapeHandler(obj)
		elif obj.NoseType == TYPE_PARABOLA:
			obj.Coefficient = 0.5
			shape = PowerShapeHandler(obj)
		elif obj.NoseType == TYPE_POWER:
			shape = PowerShapeHandler(obj)

		if shape is not None:
			shape.draw()
		else:
			obj.Shape = shape
