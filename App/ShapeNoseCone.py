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

from App.NoseConeShapeHandler import NoseConeShapeHandler
from App.NoseEllipseShapeHandler import NoseEllipseShapeHandler
from App.NoseHaackShapeHandler import NoseHaackShapeHandler
from App.NoseOgiveShapeHandler import NoseOgiveShapeHandler
from App.NoseParabolicShapeHandler import NoseParabolicShapeHandler
from App.NosePowerShapeHandler import NosePowerShapeHandler

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID

class ShapeNoseCone:

	def __init__(self, obj):
		obj.addProperty('App::PropertyLength', 'Length', 'NoseCone', 'Length of the nose not including any shoulder').Length = 60.0
		obj.addProperty('App::PropertyLength', 'Radius', 'NoseCone', 'Radius at the base of the nose').Radius = 10.0
		obj.addProperty('App::PropertyLength', 'Thickness', 'NoseCone', 'Nose cone thickness').Thickness = 2.0
		obj.addProperty('App::PropertyBool', 'Shoulder', 'NoseCone', 'Set to true if the part includes a shoulder').Shoulder = False
		obj.addProperty('App::PropertyLength', 'ShoulderLength', 'NoseCone', 'Shoulder Length').ShoulderLength = 10.0
		obj.addProperty('App::PropertyLength', 'ShoulderRadius', 'NoseCone', 'Shoulder radius').ShoulderRadius = 8.0
		obj.addProperty('App::PropertyLength', 'ShoulderThickness', 'NoseCone', 'Shoulder thickness').ShoulderThickness = 2.0
		obj.addProperty('App::PropertyFloat', 'Coefficient', 'NoseCone', 'Coefficient').Coefficient = 0.0
		obj.addProperty('App::PropertyInteger', 'Resolution', 'NoseCone', 'Resolution').Resolution = 100

		obj.addProperty('App::PropertyEnumeration', 'NoseType', 'NoseCone', 'Nose cone type')
		obj.NoseType = [TYPE_CONE,
					TYPE_ELLIPTICAL,
					TYPE_OGIVE,
					TYPE_VON_KARMAN,
					TYPE_PARABOLA,
					TYPE_PARABOLIC,
					TYPE_POWER,
					TYPE_HAACK]
		obj.NoseType = TYPE_OGIVE

		obj.addProperty('App::PropertyEnumeration', 'NoseStyle', 'NoseCone', 'Nose cone style')
		obj.NoseStyle = [STYLE_SOLID,
							STYLE_HOLLOW,
							STYLE_CAPPED]
		obj.NoseStyle = STYLE_SOLID

		obj.addProperty('Part::PropertyPartShape', 'Shape', 'NoseCone', 'Shape of the nose cone')
		obj.Proxy=self


	def execute(self, obj):
		shape = None
		if obj.NoseType == TYPE_CONE:
			shape = NoseConeShapeHandler(obj)
		elif obj.NoseType == TYPE_ELLIPTICAL:
			shape = NoseEllipseShapeHandler(obj)
		elif obj.NoseType == TYPE_OGIVE:
			shape = NoseOgiveShapeHandler(obj)
		elif obj.NoseType == TYPE_VON_KARMAN:
			obj.Coefficient = 0.0
			shape = NoseHaackShapeHandler(obj)
		elif obj.NoseType == TYPE_HAACK:
			shape = NoseHaackShapeHandler(obj)
		elif obj.NoseType == TYPE_PARABOLIC:
			shape = NoseParabolicShapeHandler(obj)
		elif obj.NoseType == TYPE_PARABOLA:
			obj.Coefficient = 0.5
			shape = NosePowerShapeHandler(obj)
		elif obj.NoseType == TYPE_POWER:
			shape = NosePowerShapeHandler(obj)

		if shape is not None:
			shape.draw()
