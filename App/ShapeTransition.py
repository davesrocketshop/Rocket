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

__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from PySide import QtGui, QtCore
import FreeCAD
import FreeCADGui
import Part

from App.TransitionConeShapeHandler import TransitionConeShapeHandler
from App.TransitionEllipseShapeHandler import TransitionEllipseShapeHandler
from App.TransitionHaackShapeHandler import TransitionHaackShapeHandler
from App.TransitionOgiveShapeHandler import TransitionOgiveShapeHandler
# from App.TransitionParabolicShapeHandler import TransitionParabolicShapeHandler
# from App.TransitionPowerShapeHandler import TransitionPowerShapeHandler

from App.Constants import TYPE_CONE, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID, STYLE_SOLID_CORE

class ShapeTransition:

	def __init__(self, obj):
		obj.addProperty('App::PropertyLength', 'Length', 'Transition', 'Length of the transition not including any shoulder').Length = 60.0
		obj.addProperty('App::PropertyLength', 'ForeRadius', 'Transition', 'Radius at the front of the transition').ForeRadius = 10.0
		obj.addProperty('App::PropertyLength', 'AftRadius', 'Transition', 'Radius at the base of the transition').AftRadius = 20.0
		obj.addProperty('App::PropertyLength', 'CoreRadius', 'Transition', 'Radius of the transition core').CoreRadius = 5.0
		obj.addProperty('App::PropertyLength', 'Thickness', 'Transition', 'Transition thickness').Thickness = 2.0
		obj.addProperty('App::PropertyBool', 'Clipped', 'Transition', 'If the transition is not clipped, then the profile is extended at the center by the corresponding radius').Clipped = True
		obj.addProperty('App::PropertyBool', 'ForeShoulder', 'Transition', 'Set to true if the part includes a forward shoulder').ForeShoulder = False
		obj.addProperty('App::PropertyLength', 'ForeShoulderLength', 'Transition', 'Forward Shoulder Length').ForeShoulderLength = 10.0
		obj.addProperty('App::PropertyLength', 'ForeShoulderRadius', 'Transition', 'Forward Shoulder radius').ForeShoulderRadius = 8.0
		obj.addProperty('App::PropertyLength', 'ForeShoulderThickness', 'Transition', 'Forward Shoulder thickness').ForeShoulderThickness = 2.0
		obj.addProperty('App::PropertyBool', 'AftShoulder', 'Transition', 'Set to true if the part includes an aft shoulder').ForeShoulder = False
		obj.addProperty('App::PropertyLength', 'AftShoulderLength', 'Transition', 'Aft Shoulder Length').AftShoulderLength = 10.0
		obj.addProperty('App::PropertyLength', 'AftShoulderRadius', 'Transition', 'Aft Shoulder radius').AftShoulderRadius = 18.0
		obj.addProperty('App::PropertyLength', 'AftShoulderThickness', 'Transition', 'Aft Shoulder thickness').AftShoulderThickness = 2.0
		obj.addProperty('App::PropertyFloat', 'Coefficient', 'Transition', 'Coefficient').Coefficient = 0.0
		obj.addProperty('App::PropertyInteger', 'Resolution', 'Transition', 'Resolution').Resolution = 100

		obj.addProperty('App::PropertyEnumeration', 'TransitionType', 'Transition', 'Transition type')
		obj.TransitionType = [TYPE_CONE,
					TYPE_ELLIPTICAL,
					TYPE_OGIVE,
					TYPE_VON_KARMAN,
					TYPE_PARABOLA,
					TYPE_PARABOLIC,
					TYPE_POWER,
					TYPE_HAACK]
		obj.TransitionType = TYPE_CONE

		obj.addProperty('App::PropertyEnumeration', 'TransitionStyle', 'Transition', 'Transition style')
		obj.TransitionStyle = [STYLE_SOLID,
                            STYLE_SOLID_CORE,
							STYLE_HOLLOW,
							STYLE_CAPPED]
		obj.TransitionStyle = STYLE_SOLID

		obj.addProperty('Part::PropertyPartShape', 'Shape', 'Transition', 'Shape of the transition')
		obj.Proxy=self


	def execute(self, obj):
		shape = None
		if obj.TransitionType == TYPE_CONE:
			shape = TransitionConeShapeHandler(obj)
		elif obj.TransitionType == TYPE_ELLIPTICAL:
		 	shape = TransitionEllipseShapeHandler(obj)
		elif obj.TransitionType == TYPE_OGIVE:
			shape = TransitionOgiveShapeHandler(obj)
		elif obj.TransitionType == TYPE_VON_KARMAN:
			obj.Coefficient = 0.0
			shape = TransitionHaackShapeHandler(obj)
		elif obj.TransitionType == TYPE_HAACK:
			shape = TransitionHaackShapeHandler(obj)
		# elif obj.TransitionType == TYPE_PARABOLIC:
		# 	shape = TransitionParabolicShapeHandler(obj)
		# elif obj.TransitionType == TYPE_PARABOLA:
		# 	obj.Coefficient = 0.5
		# 	shape = TransitionPowerShapeHandler(obj)
		# elif obj.TransitionType == TYPE_POWER:
		# 	shape = TransitionPowerShapeHandler(obj)

		if shape is not None:
			shape.draw()
