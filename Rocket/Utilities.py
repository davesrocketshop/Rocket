# ***************************************************************************
# *   Copyright (c) 2021-2025 David Carter <dcarter@davidcarter.ca>         *
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
"""General utilities for the Rocket Workbench"""

__title__ = "General utilities for the Rocket Workbench"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from typing import Any

import FreeCAD
import FreeCADGui
import math

from PySide import QtCore

# Tolerance value for effective zero
# EPSILON = 0.00000001 # 10mm^3 in m^3
EPSILON = 0.000001

def _msg(message : str) -> None:
    """Write messages to the console including the line ending."""
    FreeCAD.Console.PrintMessage(message + "\n")

def _wrn(message : str) -> None:
    """Write warnings to the console including the line ending."""
    FreeCAD.Console.PrintWarning(message + "\n")

def _err(message : str) -> None:
    """Write errors  to the console including the line ending."""
    FreeCAD.Console.PrintError(message + "\n")

def validationError(message : str) -> None:
    """
        Write errors  to the console including the line ending.
        Placeholder for future error handling
    """
    # FreeCAD.Console.PrintError(message + "\n")
    pass

def _trace(className : str, functionName : str, message : str | None = None) -> None:
    """Write errors  to the console including the line ending."""
    trace = True
    if trace:
        if message is None:
            FreeCAD.Console.PrintMessage("%s:%s()\n" % (className, functionName))
        else:
            FreeCAD.Console.PrintMessage("%s:%s(%s)\n" % (className, functionName, message))

def _toFloat(input : str, defaultValue : float = 0.0) -> float:
    if input == '':
        return defaultValue
    return float(input)

def _toInt(input : str, defaultValue : int = 0) -> int:
    if input == '':
        return defaultValue
    return int(input)

def _toBoolean(value : str) -> bool:
    if str(value).strip().lower() == "true":
        return True
    return False

def _valueWithUnits(value : str, units : str) -> str:
    ''' Converts units to user preferred '''
    qty = FreeCAD.Units.Quantity(str(value) + str(units))
    return qty.UserString

def _valueOnly(value : str, units : str) -> float:
    ''' Converts units to user preferred '''
    qty = FreeCAD.Units.Quantity(str(value) + str(units))
    return qty.Value

def reducePi(value : float) -> float:
    """ Reduce the angle x to the range -PI - PI """

    d = math.floor((value / (2 * math.pi)) + 0.5) # Round to the nearest integer
    return value - d * 2 * math.pi

def reduce2Pi(value : float) -> float:
    """ Reduce the angle x to the range 0 - 2*PI """

    d = math.floor(value / (2 * math.pi))
    return value - d * 2 * math.pi

def clamp(x : float, min : float, max : float):
    """ Clamps the value x to the range min - max. """
    if x < min:
        return min
    if x > max:
        return max
    return x


def setGroup(obj : Any) -> None:
    for property in obj.PropertiesList:
        group = obj.getGroupOfProperty(property)
        if group not in ['RocketComponent', '', 'Base']:
            print("Updating Property {0} Group {1}".format(property, group))
            obj.setGroupOfProperty(property, 'RocketComponent')

def oldMaterials() -> bool:
    ver = FreeCAD.Version()
    print("Ver %s.%s" % (ver[0], ver[1]))
    if int(ver[0]) == 0 and int(ver[1]) < 22:
        print("\told")
        return True
    print("\tnew")
    return False

def newMaterials() -> bool:
    return not oldMaterials()

def checkProgramVersion(major : int, minor : int) -> bool:
    version = FreeCAD.Version()
    print(f"Program major {version[0]}, minor {version[1]}")
    if major > int(version[0]):
        return True
    elif major == int(version[0]):
        return minor <= int(version[1])
    return False

def isFileVersion(major : int, minor : int) -> bool:
    #  Gui.ActiveDocument.Document.getProgramVersion() e.g. '0.21R33668 +7 (Git)'
    fileVersion = FreeCADGui.ActiveDocument.Document.getProgramVersion()
    print(f"File version {fileVersion}")
    base = fileVersion.split('R')
    version = base[0].split('.')
    print(f"File major {version[0]}, minor {version[1]}")
    return major == int(version[0]) and minor == int(version[1])
