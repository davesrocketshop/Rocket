# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileCopyrightText: 2025 David Carter <dcarter@davidcarter.ca>
# SPDX-File-Notice: Part of the Rocket addon.


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
            form.exec()
            return

        elif len(tubes) == 0:
            # Otherwise the user can manually enter the data
            form = DialogScalingPairs()
            form.exec()
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
            form.exec()
            return

        elif len(tubes) == 0:
            # Otherwise the user can manually enter the data
            form = DialogScaling()
            form.exec()
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
                'ToolTip': translate("Rocket", 'Matches body tube pairs suitable for scaling'),
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
                'ToolTip': translate("Rocket", 'Finds scale body tubes'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_Scaling.svg"}
