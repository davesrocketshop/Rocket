# ***************************************************************************
# *   Copyright (c) 2025 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for finding scale body tubes"""

__title__ = "FreeCAD Scaling Calculator"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from PySide import QtGui

translate = FreeCAD.Qt.translate

from Rocket.Constants import FEATURE_BODY_TUBE

from Ui.DialogScaling import DialogScaling, DialogScalingPairs

def getSelectedBodyTubes() -> list:

    # See if we have a body tube selected
    tubes = []
    for tube in FreeCADGui.Selection.getSelection():
        if tube.isDerivedFrom('Part::FeaturePython'):
            if hasattr(tube.Proxy,"Type") and tube.Proxy.Type in [FEATURE_BODY_TUBE]:
                tubes.append(tube)
            else:
                raise TypeError(translate('Rocket', "Invalid part selected"))
        else:
            raise TypeError(translate('Rocket', "Invalid part selected"))

    return tubes

def scalingPairs():
    # See if we have a type selected
    try:
        tubes = getSelectedBodyTubes()
        if len(tubes) == 2:
            form = DialogScalingPairs(tubes[0], tubes[1])
            form.exec_()
            return

        elif len(tubes) == 0:
            # Otherwise the user can manually enter the data
            form = DialogScalingPairs()
            form.exec_()
            return

        QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a pair of body tubes"))
    except TypeError as ex:
        QtGui.QMessageBox.information(None, "", str(ex))

def scalingTubes():
    # See if we have a type selected
    try:
        tubes = getSelectedBodyTubes()
        if len(tubes) == 1:
            form = DialogScaling(tubes[0])
            form.exec_()
            return

        elif len(tubes) == 0:
            # Otherwise the user can manually enter the data
            form = DialogScaling()
            form.exec_()
            return

        QtGui.QMessageBox.information(None, "", translate('Rocket', "Please select a pair of body tubes"))
    except TypeError as ex:
        QtGui.QMessageBox.information(None, "", str(ex))

class CmdScalingPairs:
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdScaling")
        FreeCADGui.doCommand("Ui.Commands.CmdScaling.scalingPairs()")

    def IsActive(self):
        # Always available, even without active document
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Match body tube pairs'),
                'ToolTip': translate("Rocket", 'Match body tube pairs suitable for scale'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Scaling.svg"}

class CmdScalingTubes:
    def Activated(self):
        FreeCADGui.addModule("Ui.Commands.CmdScaling")
        FreeCADGui.doCommand("Ui.Commands.CmdScaling.scalingTubes()")

    def IsActive(self):
        # Always available, even without active document
        return True

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Find scale body tubes'),
                'ToolTip': translate("Rocket", 'Find scale body tubes'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Scaling.svg"}
