# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-File-Notice: Part of the Rocket addon.

################################################################################
#                                                                              #
#   © 2021 David Carter <dcarter@davidcarter.ca>                               #
#                                                                              #
#   This addon is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU Lesser General Public License as             #
#   published by the Free Software Foundation, either version 2.1              #
#   of the License, or (at your option) any later version.                     #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty                #
#   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                    #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################


"""Class for editing the rocket tree"""

__title__ = "FreeCAD Body Tubes"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import FreeCADGui

from Ui.Commands.Command import Command
from Ui.Widgets.WaitCursor import WaitCursor

translate = FreeCAD.Qt.translate

def moveUp():
    for obj in FreeCADGui.Selection.getSelection():
        obj.Proxy.moveUp()

def moveDown():
    for obj in FreeCADGui.Selection.getSelection():
        obj.Proxy.moveDown()

def edit():
    for obj in FreeCADGui.Selection.getSelection():
        FreeCADGui.activeDocument().setEdit(obj.Label,0)
        return # Only process the first in the selection

def delete():
    for obj in FreeCADGui.Selection.getSelection():
        if obj.Proxy.hasParent():
            parent = obj.Proxy.getParent()
            parent.removeChild(obj)
        FreeCAD.ActiveDocument.removeObject(obj.Label)

class CmdMoveUp(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Move up")
            FreeCADGui.addModule("Ui.Commands.CmdEditTree")
            FreeCADGui.doCommand("Ui.Commands.CmdEditTree.moveUp()")
            FreeCADGui.doCommand("App.ActiveDocument.commitTransaction()")
            FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self):
        if self.partMoveableFeatureSelected():
            return True
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Move Up'),
                'ToolTip': translate("Rocket", 'Moves the object up in the rocket tree'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/button_up.svg"}

class CmdMoveDown(Command):
    def Activated(self):
        with WaitCursor():
            FreeCAD.ActiveDocument.openTransaction("Move down")
            FreeCADGui.addModule("Ui.Commands.CmdEditTree")
            FreeCADGui.doCommand("Ui.Commands.CmdEditTree.moveDown()")
            FreeCADGui.doCommand("App.ActiveDocument.commitTransaction()")
            FreeCADGui.doCommand("App.activeDocument().recompute(None,True,True)")

    def IsActive(self):
        if self.partMoveableFeatureSelected():
            return True
        return False

    def GetResources(self):
        return {'MenuText': translate("Rocket", 'Move Down'),
                'ToolTip': translate("Rocket", 'Moves the object down in the rocket tree'),
                'Pixmap': FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/button_down.svg"}
