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
"""Base class for rocket component events"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

class Type():
    value = None
    name = None

    def __init__(self, _value, _name):
        self.value = _value
        self.name = _name
		
    def matches(self, testValue):
        return (0 != (self.value & testValue ))

ERROR = Type(-1, "Error")
NON_FUNCTIONAL = Type(1, "nonFunctional")
MASS = Type(2, "Mass")
AERODYNAMIC = Type(4, "Aerodynamic")
TREE = Type( 8, "TREE")
UNDO = Type( 16, "UNDO")
MOTOR = Type( 32, "Motor")
EVENT = Type( 64, "Event")
TEXTURE = Type( 128, "Texture")
GRAPHIC = Type( 256, "Configuration")

class ComponentChangeEvent(): # extends EventObject {

    # A change that does not affect simulation results in any way (name, color, etc.)
    NONFUNCTIONAL_CHANGE = NON_FUNCTIONAL.value
    # A change that affects the mass properties of the rocket
    MASS_CHANGE = MASS.value
    # A change that affects the aerodynamic properties of the rocket
    AERODYNAMIC_CHANGE = AERODYNAMIC.value
    # A change that affects the mass and aerodynamic properties of the rocket
    AEROMASS_CHANGE = (MASS.value | AERODYNAMIC.value )
    BOTH_CHANGE = AEROMASS_CHANGE  # syntactic sugar / backward compatibility


    # A change that affects the rocket tree structure
    TREE_CHANGE = TREE.value
    # A change caused by undo/redo.
    UNDO_CHANGE = UNDO.value
    # A change in the motor configurations or names
    MOTOR_CHANGE = MOTOR.value
    # A change that affects the events occurring during flight.
    EVENT_CHANGE = EVENT.value
    # A change to the 3D texture assigned to a component
    TEXTURE_CHANGE = TEXTURE.value
    # when a flight configuration fires an event, it is of this type
    # UI-only change, but does not effect the true
    GRAPHIC_CHANGE = GRAPHIC.value
	
			
    component = None
    type = None
	
    def __init__(self, component, eventType):
        self.component = component
        if eventType is None or eventType == ERROR:
            raise ValueError("no event type provided")
        self.type = eventType.value	

    # public static TYPE getTypeEnum( final int typeNumber ){
    #     for( TYPE ccet : ComponentChangeEvent.TYPE.values() ){
    #         if( ccet.value == typeNumber ){
    #             return ccet;
    #         }
    #     }
    #     throw new IllegalArgumentException(" type number "+typeNumber+" is not a valid Type enum...");
    # }

    # Return the source component of this event as specified in the constructor.
    def getSource(self):
        return self.component

    def isAerodynamicChange(self):
        return AERODYNAMIC.matches(self.type)

    def isEventChange(self):
        return EVENT.matches(self.type)

    def isFunctionalChange(self):
        return not self.isNonFunctionalChange()

    def isNonFunctionalChange(self):
        return NON_FUNCTIONAL.matches(self.type)

    def isMassChange(self):
        return MASS.matches(self.type)

    def isTextureChange(self):
        return TEXTURE.matches(self.type)

    def isTreeChange(self):
        return TREE.matches(self.type)

    def isUndoChange(self):
        return UNDO.matches(self.type)


    def isMotorChange(self):
        return MOTOR.matches(self.type)

    def getType(self):
        return self.type

    def __str__(self):
        s = ""
        
        if self.isNonFunctionalChange():
            s += ",nonfunc"
        if self.isMassChange():
            s += ",mass"
        if self.isAerodynamicChange():
            s += ",aero"
        if self.isTreeChange():
            s += ",tree"
        if self.isUndoChange():
            s += ",undo"
        if self.isMotorChange():
            s += ",motor"
        if self.isEventChange():
            s += ",event"
        
        if s.length() > 0:
            s = s[1:]
        
        return "ComponentChangeEvent[" + s + "]"
